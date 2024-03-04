# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
codeproj - projectteam core
"""
# 原生
import logging

# 第三方 import
from django.db import IntegrityError

# 项目内 import
from apps.authen.models import Organization
from apps.codeproj import models
from util import errcode
from util.exceptions import ProjectTeamCreateError, ProjectTeamLabelCreateError, ProjectTeamLabelUpdateError, \
    ProjectTeamUpdateError
from util.operationrecord import OperationRecordHandler

logger = logging.getLogger(__name__)


class ProjectTeamManager(object):
    """项目团队管理
    """

    @classmethod
    def init_project_team(cls, org, name):
        """创建项目团队
        """
        try:
            return models.ProjectTeam.objects.create(organization=org, name=name)
        except IntegrityError:
            logger.error("[Org: %s][Name: %s] project team exist", org, name)
            return None

    @classmethod
    def create_project_team(cls, org, name, user, **kwargs):
        """创建项目
        :param org: Organization, 团队
        :param name: str, 团队名称
        :param user: User, 操作人
        :params kwargs: 其他参数
        :return: project_team
        """
        project_team = cls.init_project_team(org, name)
        if not project_team:
            raise ProjectTeamCreateError(errcode.E_SERVER_PROJECT_TEAM_EXIST, "项目已存在")
        project_team.display_name = kwargs.get("display_name") or project_team.name
        project_team.description = kwargs.get("description")
        project_team.creator = user
        project_team.save(user=user)
        # 将创建人加入项目管理员中
        project_team.assign_perm(user, models.ProjectTeam.PermissionEnum.ADMIN)
        return project_team

    @classmethod
    def update_project_team(cls, pt, name, user, **kwargs):
        """更新项目团队信息
        :param pt: ProjectTeam, 项目
        :param name: str，项目name
        :param user: User, 操作人
        :params kwargs: 其他参数
        :return: project_team
        """
        if name != pt.name and models.ProjectTeam.objects.filter(
                organization=pt.organization, name=name).exclude(id=pt.id).exists():
            raise ProjectTeamUpdateError(errcode.E_SERVER_PROJECT_TEAM_EXIST, "项目组名称重复，请调整后重试")
        if pt.name != name:
            kwargs["name"] = name
        pt.name = name
        pt.display_name = kwargs.get("display_name", pt.display_name)
        pt.description = kwargs.get("description", pt.description)
        pt.status = kwargs.get("status", pt.status)
        pt.save(user=user)
        OperationRecordHandler.add_projectteam_operation_record(pt, "更新项目组", user, "更新参数为: %s" % kwargs)
        return pt

    @classmethod
    def set_project_team_status(cls, pt, user, status):
        """将项目团队标记为禁用
        :param pt: ProjectTeam, 项目
        :param user: User, 操作人
        :param status: int, 项目组状态
        :return: project_team
        """
        if status == models.ProjectTeam.StatusEnum.DISACTIVE:
            action = "禁用项目组"
        else:
            action = "恢复项目组"
        pt.status = status
        pt.save(user=user)
        OperationRecordHandler.add_projectteam_operation_record(
            pt, action, user, "标记项目组状态为%s" % status)
        return pt

    @classmethod
    def get_user_teams(cls, org, user, perm=None):
        """获取用户有权限的、管理的、仅为成员的项目，团队管理员可获取全部项目
        :param org: Organization, 组织
        :param user: User, 访问用户
        :param perm: 权限，默认为None
        :return: teams, perm为None时返回用户有权限的项目
        """
        queryset = models.ProjectTeam.objects.filter(organization=org)
        if user.has_perm(Organization.PermissionNameEnum.CHANGE_ORG_PERM, org):
            # 团队管理员默认获取全部项目
            return queryset
        permission_choices = dict(Organization.PERMISSION_CHOICES)
        related_ids = []
        for group in user.groups.filter(name__startswith="team_"):
            _, team_id, perm_name = group.name.split('_')
            if team_id not in related_ids:
                if not perm or permission_choices[perm] == perm_name:
                    related_ids.append(team_id)
        return queryset.filter(id__in=related_ids)

    @classmethod
    def add_team_members(cls, pt, users, perm):
        """增加项目组成员
        :param pt: ProjectTeam, 项目组
        :param users: List<User> user 列表
        :param perm: int, 角色
        """
        if perm == models.ProjectTeam.PermissionEnum.ADMIN or perm == models.ProjectTeam.PermissionEnum.USER:
            for user in users:
                # 仅能添加团队内的成员
                if user.has_perm("view_organization", pt.organization):
                    pt.assign_perm(user, perm)


class LabelManager(object):
    """标签管理
    """

    @classmethod
    def init_label(cls, project_team, name):
        """创建项目团队
        """
        if models.Label.objects.filter(project_team=project_team, name=name).exists():
            logger.error("[ProjectTeam: %s][Name: %s] label team exist", project_team, name)
            return None
        return models.Label.objects.create(project_team=project_team, name=name)

    @classmethod
    def create_label(cls, project_team, name, user, **kwargs):
        """创建项目组标签
        :param project_team: ProjectTeam, 项目组
        :param name: str, 标签名称
        :param user: User, 操作人
        :params kwargs: 其他参数
        """
        label = cls.init_label(project_team, name)
        if not label:
            raise ProjectTeamLabelCreateError(errcode.E_SERVER_LABEL_EXIST, "标签已存在")
        label.creator = user
        label.parent_label = kwargs.get("parent_label", label.parent_label)
        label.description = kwargs.get("description", label.description)
        # 获取平级index最大的一个label
        max_index_label = models.Label.objects.filter(project_team=label.project_team,
                                                      parent_label=label.parent_label) \
            .exclude(id=label.id).order_by("-index").first()
        label.index = max_index_label.index + 1 if max_index_label else 0
        label.save(user=user)
        return label

    @classmethod
    def update_label(cls, label, name, user, **kwargs):
        """更新项目组标签
        :param label: Label, 标签
        :param name: str, 标签名称
        :param user: User, 操作人
        :params kwargs: 其他参数
        :return: label
        """
        if name != label.name and models.Label.objects.filter(
                project_team=label.project_team, name=name).exclude(id=label.id).exists():
            raise ProjectTeamLabelUpdateError(errcode.E_SERVER_LABEL_EXIST, "标签名已存在，请调整后重试")
        if label == kwargs.get("parent_label"):
            raise ProjectTeamLabelUpdateError(errcode.E_SERVER_LABEL_CYCLE_REF, "父标签不可引用自己")
        label.name = name
        label.description = kwargs.get("description", label.description)
        temp_parent_label = label.parent_label
        temp_index = label.index
        label.parent_label = kwargs.get("parent_label", temp_parent_label)
        label.index = kwargs.get("index", temp_index)
        label.save(user=user)
        # 当标签索引发生变更，或层级发生改变时，重新排列该标签同级标签顺序
        if temp_index != label.index or temp_parent_label != label.parent_label:
            cls.order_labels_by_label(label)
        return label

    @classmethod
    def order_labels_by_label(cls, cur_label):
        """根据当前label进行同级labels排序
        :param cur_label: Label, 当前标签
        """
        # 获取同级其他标签
        labels = models.Label.objects.filter(project_team=cur_label.project_team,
                                             parent_label=cur_label.parent_label) \
            .exclude(id=cur_label.id).order_by("index")
        index = 0
        for label in labels:
            if index == cur_label.index:
                index += 1
            if label.index != index:
                label.index = index
                label.save()
            index += 1

    @classmethod
    def delete_label(cls, label):
        """删除标签，server进行联级删除
        :param label: Label, 标签
        """
        children_labels = models.Label.objects.filter(project_team=label.project_team, parent_label=label)
        for children_label in children_labels:
            cls.delete_label(children_label)
        label.delete(permanent=True)

    @classmethod
    def _get_label_dict(cls, label):
        """获取label的json结构
        :param label: Label, 标签
        :return: dict
        """
        return {
            "id": label.id,
            "name": label.name,
            "parent_label": label.parent_label_id,
            "index": label.index,
            "description": label.description,
            "children": []
        }

    @classmethod
    def _build_tree(cls, labels):
        """递归构建标签树结构
        :param labels: List<Label>, 标签列表
        :return: 标签树tree, dict
        """
        tree = []
        labels = labels.order_by("index")
        for label in labels:
            label_dict = cls._get_label_dict(label)
            children_labels = models.Label.objects.filter(project_team=label.project_team, parent_label=label)
            if children_labels.count() > 0:
                label_dict["children"].append(cls._build_tree(children_labels))
            tree.append(label_dict)
        return tree

    @classmethod
    def get_pt_label_tree(cls, project_team):
        """获取项目组树状标签
        :param project_team: ProjectTeam, 项目组
        :return: 项目组标签树tree, dict
        """
        labels = models.Label.objects.filter(project_team=project_team, parent_label__isnull=True)
        return cls._build_tree(labels)
