# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
base - basemodel
提供虚拟model基类
Common model behavior for all models.
Soft-deletion (including cascade) and tracking of user and timestamp for model
creation, modification, and soft-deletion.
"""

import logging

from django.db import models, router, IntegrityError
from django.db.models.deletion import Collector
from django.db.models.query import QuerySet
from django.core.cache import cache
from django.core.exceptions import FieldError
from django.utils import timezone

logger = logging.getLogger(__name__)


class BasePerm(object):
    """对象权限操作
    """

    class PermissionEnum:
        ADMIN = 1
        USER = 2

    PERMISSION_CHOICES = (
        (PermissionEnum.ADMIN, "Admin"),
        (PermissionEnum.USER, "User")
    )

    def _get_group(self, perm):
        """获取指定权限的组织
        """
        raise NotImplementedError

    def get_members(self, perm):
        group = self._get_group(perm)
        users = group.user_set.all()
        return users

    def assign_perm(self, user, perm):
        group = self._get_group(perm)
        try:
            user.groups.add(group)
        except IntegrityError:
            pass

    def assign_members_perm(self, users, perm):
        group = self._get_group(perm)
        for user in users:
            try:
                user.groups.add(group)
            except IntegrityError:
                pass

    def remove_perm(self, user, perm):
        group = self._get_group(perm)
        try:
            user.groups.remove(group)
        except IntegrityError:
            pass


class ConcurrencyError(Exception):
    pass


def utcnow(date=False):
    """获得utc时间或日期"""
    if not date:
        return timezone.now()
    return timezone.now().date()


def localnow(date=False):
    """获得北京时间或日期"""
    if not date:
        return timezone.localtime()
    return timezone.localtime().date()


class SoftDeleteCollector(Collector):
    """
    A variant of Django's default delete-cascade collector that implements soft
    delete.
    """

    def collect(self, objs, *args, **kwargs):
        """
        Collect ``objs`` and dependent objects.
        We override in order to store "root" objects for undelete.
        """
        if kwargs.get("source", None) is None:
            self.root_objs = objs
        super(SoftDeleteCollector, self).collect(objs, *args, **kwargs)

    def delete(self, user=None):
        """
        Soft-delete all collected instances.
        """
        now = utcnow()
        for model, instances in self.data.items():
            pk_list = [obj.pk for obj in instances]
            try:
                model._base_manager.filter(
                    pk__in=pk_list, deleted_time__isnull=True).update(
                    deleter=user, deleted_time=now)
            except FieldError:
                if not issubclass(model, CDBaseModel):
                    pass  # 非CDBaseModel不存在deleted_time，故不做处理
                else:
                    raise  # CDBaseModel子类抛异常表示数据库不同步

    def undelete(self, user=None):
        """
        Undelete all collected instances that were deleted.
        """
        # timestamps on which root obj(s) were deleted; only cascade items also
        # deleted in one of these same cascade batches should be undeleted.
        deletion_times = set([o.deleted_time for o in self.root_objs])
        for model, instances in self.data.items():
            pk_list = [obj.pk for obj in instances]
            model._base_manager.filter(
                pk__in=pk_list, deleted_time__in=deletion_times).update(
                deleter=None, deleted_time=None)


class MTQuerySet(QuerySet):
    """
    Implements modification tracking and soft deletes on bulk update/delete.
    """

    def create(self, *args, **kwargs):
        """
        Creates, saves, and returns a new object with the given kwargs.
        """
        user = kwargs.pop("user", None)
        if user:
            kwargs["creator"] = user
            kwargs["modifier"] = user
        return super(MTQuerySet, self).create(*args, **kwargs)

    def update(self, *args, **kwargs):
        """
        Update all objects in this queryset with modifications in ``kwargs``.
        """
        if not kwargs.pop("notrack", False):
            kwargs["modifier"] = kwargs.pop("user", None)
            kwargs["modified_time"] = utcnow()
        return super(MTQuerySet, self).update(*args, **kwargs)

    def delete(self, user=None, permanent=False):
        """
        Soft-delete all objects in this queryset, unless permanent=True.
        """
        if permanent:
            return super(MTQuerySet, self).delete()
        collector = SoftDeleteCollector(using=self.db)
        collector.collect(self)
        collector.delete(user)

    def undelete(self, user=None):
        """
        Undelete all objects in this queryset.
        """
        collector = SoftDeleteCollector(using=self.db)
        collector.collect(self)
        collector.undelete(user)


class MTManager(models.Manager):
    """
    Manager using ``MTQuerySet`` and optionally hiding deleted objects.
    By making show_deleted an instantiation argument, and defaulting it to
    False, we can achieve something a bit subtle: the instantiated default
    manager on a MTModel shows all objects, including deleted one (meaning the
    admin will show deleted objects, so they can be undeleted). But
    related-object managers (which subclass the default manager class) will
    still hide deleted objects.
    """

    def __init__(self, *args, **kwargs):
        """Instantiate a MTManager, pulling out the ``show_deleted`` arg."""
        self._show_deleted = kwargs.pop("show_deleted", False)
        super(MTManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        """Return a ``MTQuerySet`` for all queries."""
        qs = MTQuerySet(self.model, using=self.db)
        if not self._show_deleted:
            qs = qs.filter(deleted_time__isnull=True)
        return qs


class CDBaseModel(models.Model):
    """
    Common base abstract model for all MozTrap models.
    Tracks user and timestamp for creation, modification, and (soft) deletion.
    """
    created_time = models.DateTimeField(db_index=True, default=utcnow, verbose_name='创建时间')
    creator = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name="+", on_delete=models.SET_NULL, verbose_name='创建人')

    modified_time = models.DateTimeField(db_index=True, default=utcnow, verbose_name='最近修改时间')
    modifier = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name="+", on_delete=models.SET_NULL, verbose_name='最近修改人')
    deleted_time = models.DateTimeField(db_index=True, blank=True, null=True, verbose_name='删除时间')
    deleter = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name="+", on_delete=models.SET_NULL, verbose_name='删除人')

    # default manager returns all objects, so admin can see all
    everything = MTManager(show_deleted=True)
    # ...but "objects", for use in most code, returns only not-deleted
    objects = MTManager(show_deleted=False)

    @classmethod
    def delete_modelfilter_choices_cache(cls, model):
        cache_key = 'modelfilter-choices-%s' % (model._meta,)
        cache.delete(cache_key)

    def save(self, *args, **kwargs):
        """
        Save this instance.
        Records modified timestamp and user, and raises ConcurrencyError if an
        out-of-date version is being saved.
        """
        self.delete_modelfilter_choices_cache(self)

        if not kwargs.pop("notrack", False):
            user = kwargs.pop("user", None)
            now = utcnow()
            if self.pk is None and user is not None:
                self.creator = user
            # .create() won't pass in user, but presets modifier
            if not (self.pk is None and self.modifier is not None):
                self.modifier = user
            self.modified_time = now

        # MTModels always have an auto-PK and we don't set PKs explicitly, so
        # we can assume that a set PK means this should be an update.
        if kwargs.get("force_update") or self.id is not None:
            non_pks = [f for f in self._meta.local_fields if not f.primary_key]
            # This isn't a race condition because the save will only take
            # effect if previous_version is actually up to date.
            values = [(f, None, f.pre_save(self, False)) for f in non_pks]
            rows = self.__class__.objects.filter(id=self.id)._update(values)
            if not rows:
                raise ConcurrencyError(
                    "No {0} row with id {1} and version {2} updated.".format(
                        self.__class__, self.id, '?')
                )
        else:
            return super(CDBaseModel, self).save(*args, **kwargs)

    def clone(self, cascade=None, overrides=None, user=None):
        """
        Clone this instance and return the new, cloned instance.
        ``overrides`` should be a dictionary of override values for fields on
        the cloned instance.
        M2M or reverse FK relations listed in ``cascade`` iterable will be
        cascade-cloned. By default, if not listed in ``cascade``, m2m/reverse
        FKs will effectively be cleared (as the remote object will still be
        pointing to the original instance, not the cloned one.)
        If ``cascade`` is a dictionary, keys are m2m/reverse-FK accessor names,
        and values are a callable that takes the queryset of all related
        objects and returns those that should be cloned.
        """
        if cascade is None:
            cascade = {}
        else:
            try:
                cascade.items
            except AttributeError:
                cascade = dict((i, lambda qs: qs) for i in cascade)

        if overrides is None:
            overrides = {}

        overrides["created_time"] = utcnow()
        overrides["creator"] = user
        overrides["modifier"] = user

        clone = self.__class__()

        for field in self._meta.fields:
            if field.primary_key:
                continue
            val = overrides.get(field.name, getattr(self, field.name))
            setattr(clone, field.name, val)

        clone.save(force_insert=True)

        for name, filter_func in cascade.items():
            mgr = getattr(self, name)
            if mgr.__class__.__name__ == "ManyRelatedManager":  # M2M
                clone_mgr = getattr(clone, name)
                existing = set(clone_mgr.all())
                new = set(filter_func(mgr.all()))
                clone_mgr.add(*new.difference(existing))
                clone_mgr.remove(*existing.difference(new))
            elif mgr.__class__.__name__ == "RelatedManager":  # reverse FK
                reverse_name = getattr(self.__class__, name).related.field.name
                for obj in filter_func(mgr.all()):
                    obj.clone(overrides={reverse_name: clone})
            else:
                raise ValueError(
                    "Cannot cascade-clone '{0}'; "
                    "not a many-to-many or reverse foreignkey.".format(name))

        return clone

    def delete(self, user=None, permanent=False):
        """
        (Soft) delete this instance, unless permanent=True.
        """
        if permanent:
            return super(CDBaseModel, self).delete()
        self._collector.delete(user)

    def undelete(self, user=None):
        """
        Undelete this instance.
        """
        self._collector.undelete(user)

    @property
    def _collector(self):
        """Returns populated delete-cascade collector."""
        db = router.db_for_write(self.__class__, instance=self)
        collector = SoftDeleteCollector(using=db)
        collector.collect([self])
        return collector

    class Meta:
        abstract = True
