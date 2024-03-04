# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""项目通用逻辑
"""
# 原生 import
import logging
import random
import string
import time

# 第三方 import
from django.db import transaction
from django.utils import timezone

# 项目内 import
from apps.authen.models import CodeDogUser, Organization, OrganizationPermissionApply
from util.cipher import Base62Cipher, CaesarCipher
from util.exceptions import InviteCodeError, OrganizationCreateError, errcode
from util.operationrecord import OperationRecordHandler
from util.shortuuid import ShortIDGenerator

logger = logging.getLogger(__file__)


class BaseOrganizationManager(object):
    """组织管理
    """

    @classmethod
    def get_org_sid(cls, count=3):
        """获取组织短编号
        """
        num = 0
        while num < count:
            org_sids = [ShortIDGenerator.generate_short_id_v1() for _ in range(50)]
            exist_org_sids = list(Organization.objects.filter(org_sid__in=org_sids).values_list("org_sid", flat=True))
            new_org_ids = list(set(org_sids) - set(exist_org_sids))
            if new_org_ids:
                return new_org_ids[0]
            num += 1
            logger.info("[Retry: %s/%s] create org sid failed, continue...", num, count)

    @classmethod
    def create_org(cls, name, user, **kwargs):
        """创建组织
        :param name: str, 团队名称
        :param user: User, 操作人
        :params kwargs: 其他参数
        """
        level_org_count_choices = dict(CodeDogUser.LEVEL_ORG_COUNT_CHOICES)
        if Organization.objects.filter(creator=user).count() >= level_org_count_choices[user.codedoguser.level]:
            raise OrganizationCreateError(
                errcode.E_SERVER_ORGANIZATION_CREATE_OUT_LIMIT, "当前用户创建团队数量已经达到上限，无法继续创建")
        status = OrganizationPermissionApply.ApplyStatusEnum.CHECKED
        check_result = OrganizationPermissionApply.CheckResultEnum.PASS
        apply_msg = "自动通过，无需审核"
        org_sid = cls.get_org_sid()
        org = Organization.objects.create(
            org_sid=org_sid, name=name, user=user,
            address=kwargs.get("address"),
            owner=kwargs.get("owner"),
            business_license=kwargs.get("business_license"),
            tel_number=kwargs.get("tel_number"),
            description=kwargs.get("description"),
            status=Organization.StatusEnum.ACTIVE
        )
        org.assign_perm(user, Organization.PermissionEnum.ADMIN)
        OrganizationPermApplyManager.create_org_apply(org, user, apply_msg, status=status, check_result=check_result)
        return org

    @classmethod
    def get_user_orgs(cls, user, perm=None):
        """获取用户有权限的、管理的、仅为成员的团队
        :param user: User, 访问用户
        :param perm: 权限，默认为None
        :return: orgs, perm为None时返回用户有权限的团队
        """
        permission_choices = dict(Organization.PERMISSION_CHOICES)
        related_orgs = []
        for group in user.groups.filter(name__startswith="org_"):
            _, org_id, perm_name = group.name.split('_')
            if org_id not in related_orgs:
                if not perm or permission_choices[perm] == perm_name:
                    related_orgs.append(org_id)
        return Organization.objects.filter(id__in=related_orgs).exclude(status=Organization.StatusEnum.FORBIDEN)

    @classmethod
    def check_user_org_perm(cls, user, org=None, org_sid=None, perm=None):
        """检查用户是否有指定团队的权限
        """
        if not org and not org_sid:
            return False
        if not org:
            org = Organization.objects.filter(org_sid=org_sid).first()
        if not org:
            return False
        if not perm:
            perm = Organization.PermissionNameEnum.VIEW_ORG_PERM
        return user.has_perm(perm, org)

    @classmethod
    def update_org_status(cls, org, user, status):
        """对团队进行审核操作，仅平台管理员可操作
        :param org: Organization, 团队
        :param user: User, 审核人
        :param status: int, 审核状态
        """
        if user.is_superuser:
            org.status = status
            org.save()
            OperationRecordHandler.add_organization_operation_record(
                org, "团队审核", user, "审核结果: %s-%s" % (status, Organization.STATUSENUM_DICT[status]))

    @classmethod
    def update_org_level(cls, org, user, level):
        """更新团队级别，仅平台管理员可操作
        :param org: Organization, 团队
        :param user: User, 审核人
        :param level: int, 级别
        """
        if user.is_superuser:
            old_level = org.level
            org.level = level
            org.save()
            OperationRecordHandler.add_organization_operation_record(
                org, "团队级别变更", user, "变更情况: %s-%s -> %s-%s" % (
                    old_level, Organization.LEVELENUM_DICT[old_level], level, Organization.LEVELENUM_DICT[level]))

    @classmethod
    def get_invite_code(cls, org, perm, user):
        """根据角色类型生成团队邀请码
        :param org: Organization, 组织
        :param perm: 角色，1 管理员，2 普通成员
        :param user: User, 发出邀请的用户
        :return: code 邀请码
        """
        """
        参考https://linsir.org/post/Creat-the-unique-activation-code-with-python/
        随机大小写字母Rr + org_id_code + T + 时间戳t_62位 + perm_code + "特殊字符" + username_code
        Rr : 随机大小写字母
        org_id_code : 先hex(org_id)，然后凯撒加密，key是perm
        T : Rr凯撒加密，key是perm，必须大写，因为要根据这个隔开前后(perm_code的大写)
        时间戳t_62位：62进制-10个6 然后凯撒加密，key是perm+id, 然后倒序
        perm_code：只能是0-9,且必须是最后一位。这里是Rr凯撒加密，key是perm
        special_char : 随机一个标点符号隔开
        username_code:对user进行凯撒加密, key是perm
        """

        # 参考yorkie 登录服务邀请码实现机制
        caesar_cipher = CaesarCipher()
        base62_cipher = Base62Cipher()

        # 生成随机字母
        Rr = random.choice(string.ascii_uppercase + string.ascii_lowercase)
        # org_id加密，key采用perm
        org_id_hex = hex(org.id)[2:]  # 获取16进制后面的值
        org_id_code = caesar_cipher.encrypt_text(str(org_id_hex), perm)
        # 获取T，对Rr加密，key采用perm，并大写（注：必须大写，需要根据T进行前后分割）
        perm_code = caesar_cipher.encrypt_text(Rr, perm)  # 可通过Rr加密后的内容获取出key，即perm
        T = perm_code.upper()
        # 前缀部分
        prefix = Rr + org_id_code + T

        # 时间戳加密，key采用org.id与perm结合，并逆序
        # 邀请码过期时间1000 * 60 * 10 默认10分钟
        expired_time = 1000 * 60 * 10
        timestamp = int(time.time() * 1000) - 6666666666 * perm + expired_time
        timestamp_text = caesar_cipher.encrypt_text(base62_cipher.int_to_str62(timestamp), perm + org.id)[::-1]
        # 生成随机特殊字符
        special_char = random.choice(string.punctuation)
        # username加密，key采用perm
        username_code = caesar_cipher.encrypt_text(user.username, perm)

        # 生成code
        code = prefix + timestamp_text + perm_code + special_char + username_code
        return code

    @classmethod
    def decode_invite_code(cls, invite_code):
        """对团队邀请码进行解码操作
        :param invite_code: 根据get_invite_code获取的邀请码
        :return: org_id, perm, username
        """
        try:
            # 参考yorkie 登录服务邀请码实现机制
            caesar_cipher = CaesarCipher()
            base62_cipher = Base62Cipher()
            # 特殊字符前后处理
            decode_code = None
            for special_char in string.punctuation:
                if special_char in invite_code:
                    decode_code = invite_code.split(special_char)
                    break
            if not decode_code:
                # 兼容空字符串，据yorkie之前说的，前端可能传递到后端的特殊字符变成了' '，因此兼容处理
                decode_code = invite_code.split(' ')

            # 根据 => 随机大小写字母Rr + org_id_code + T + 时间戳t_62位 + perm_code + "特殊字符" + username_code
            # 前置内容
            pre_code = decode_code[0]
            # 随机大小写字母Rr
            Rr = pre_code[0]
            perm_code = pre_code[-1]
            T = perm_code.upper()
            # org_id_code + T + 时间戳t_62位
            temp_coode = pre_code[1:-1].split(T)
            org_id_code = temp_coode[0]
            timestamp_text = temp_coode[1]

            # 通过Rr获取perm_code加密的key值，得到真实的perm
            # 解码获取角色权限
            perm = ord(perm_code) - ord(Rr) if ord(perm_code) >= ord(Rr) else ord(perm_code) - ord(Rr) + 26

            # 解码获取团队ID
            org_id_hex = caesar_cipher.decrypt_text(org_id_code, perm)
            org_id = str(int(org_id_hex.upper(), 16))

            # 解码获取时间戳
            timestamp = caesar_cipher.decrypt_text(timestamp_text[::-1], int(org_id) + int(perm))
            old_timestamp = base62_cipher.str62_to_int(timestamp) + 6666666666 * perm

            # 对邀请用户解码
            username_code = decode_code[1]
            username = caesar_cipher.decrypt_text(username_code, perm)
        except Exception as e:
            logger.exception("邀请码错误，invite_code：%s，Exception：%s" % (invite_code, e))
            raise InviteCodeError()
        cur_timestamp = time.time() * 1000
        if cur_timestamp > old_timestamp:
            raise InviteCodeError(code=errcode.E_SERVER_INVITE_CODE_EXPIRED)
        return org_id, perm, username


class OrganizationManager(BaseOrganizationManager):
    pass


class BaseOrganizationPermApplyManager(object):
    """团队申请单管理
    """

    @classmethod
    def create_org_apply(cls, org, user, apply_msg,
                         status=OrganizationPermissionApply.ApplyStatusEnum.CHECKING,
                         check_result=OrganizationPermissionApply.CheckResultEnum.NO_PASS):
        """创建团队申请单
        :param org: Organization, 团队
        :param user: User, 操作人
        :param apply_msg: str, 申请理由
        :param status: int, 申请状态
        :param check_result: int, 检查状态
        """
        check_time = None
        if check_result == OrganizationPermissionApply.CheckResultEnum.PASS:
            check_time = timezone.now()
        instance = OrganizationPermissionApply.objects.create(
            organization=org, applicant=user, apply_msg=apply_msg,
            status=status, check_result=check_result, check_time=check_time
        )
        return instance

    @classmethod
    def update_org_apply(cls, org, user, apply_msg):
        """如果团队审核中，则直接更新申请单，如果未审核通过，则需创建申请单
        :param org: Organization, 团队
        :param user: User, 操作人
        :param apply_msg: str, 申请理由
        """
        # 团队未激活
        if not org.validate_org_checked():
            # 获取该团队最新的申请单
            apply = OrganizationPermissionApply.objects.filter(organization=org).last()
            # 团队无申请单，或申请单审核完成未通过，此时更新团队信息时需要创建新的审批单
            # 注：未处理取消申请状态的操作，按流程暂时不会存在取消申请状态
            if not apply or apply.is_checked_and_no_pass():
                cls.create_org_apply(org, user, apply_msg)
            # 团队申请单处于审核中，却申请理由变更，需要更新申请单
            if apply and apply.is_checking() and apply.apply_msg != apply_msg:
                apply.apply_msg = apply_msg
                apply.save()

    @classmethod
    def check_org(cls, apply_id, checker, check_result=None, check_remark=None, **kwargs):
        """审核团队
        """
        org_perm_apply = OrganizationPermissionApply.objects.get(id=apply_id)
        if not org_perm_apply.is_checking():
            logger.info("[Org: %s][Applicant: %d][status: %d] apply has been checked/canceled",
                        org_perm_apply.organization, org_perm_apply.applicant_id, org_perm_apply.status)

        with transaction.atomic():
            org = org_perm_apply.organization
            if check_result == OrganizationPermissionApply.CheckResultEnum.PASS:
                # 审批通过时，调整团队状态
                org.status = Organization.StatusEnum.ACTIVE
            else:  # 审批未通过
                org.status = Organization.StatusEnum.DISACTIVE
            org.save()
            OrganizationPermissionApply.objects.select_for_update().filter(id=apply_id).update(
                checker=checker, check_result=check_result,
                check_remark=check_remark, check_time=timezone.now(), status=org_perm_apply.ApplyStatusEnum.CHECKED)
        org_perm_apply.refresh_from_db()
        return org_perm_apply


class OrganizationPermApplyManager(BaseOrganizationPermApplyManager):
    pass
