# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
scan_conf - base serializers
"""
import logging

# 第三方
from rest_framework import serializers

# 项目内
from apps.scan_conf import models, core
from apps.scan_conf.core.toolmgr import CheckToolManager
from apps.scan_conf.core.toollibmgr import ToolLibManager
from apps.base.serializers import CDBaseModelSerializer
from apps.authen.serializers.base import ScmAuthCreateSerializer
from apps.codeproj.core import ScmAuthManager

logger = logging.getLogger(__name__)


class OnlySuperAdminReadField(serializers.Field):
    """仅超级管理员可见的字段
    """

    def __init__(self, **kwargs):
        kwargs['read_only'] = True
        super().__init__(**kwargs)

    def to_representation(self, value):
        request = self.context.get("request")
        if request and request.user and request.user.is_superuser:
            return value
        else:
            return ""


class LanguageSerializer(serializers.ModelSerializer):
    """语言序列化
    """
    display_name = serializers.CharField(source="get_name_display")

    class Meta:
        model = models.Language
        fields = "__all__"


class LabelSerializer(serializers.ModelSerializer):
    """标签序列化
    """
    checked = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    def get_checked(self, label):
        return "基础" in label.name

    def get_display_name(self, label):
        if "规范" in label.name:
            return "腾讯代码规范"
        else:
            return "%s扫描" % label.name

    class Meta:
        model = models.Label
        fields = "__all__"


class CheckRuleDescSerializer(serializers.ModelSerializer):
    """规则描述序列化
    """

    class Meta:
        model = models.CheckRuleDesc
        fields = ["desc_type", "desc"]


class CheckToolSimpleSerializer(serializers.ModelSerializer):
    """工具简单序列化
    """
    display_name = serializers.SerializerMethodField()
    scope = serializers.SerializerMethodField()
    name = OnlySuperAdminReadField()

    def get_display_name(self, checktool):
        """获取工具展示名称
        """
        request = self.context.get("request")
        user = request.user if request else None
        return checktool.get_show_name(user=user)

    def get_scope(self, checktool):
        """公有True/私有False工具
        """
        if checktool.is_public():
            return models.CheckTool.ScopeEnum.PUBLIC
        return models.CheckTool.ScopeEnum.PRIVATE

    class Meta:
        model = models.CheckTool
        fields = ["id", "name", "display_name", "scope", "status", "show_display_name", "build_flag"]


class ChoicesField(serializers.Field):
    def __init__(self, choices, **kwargs):
        self._choices = dict(choices)
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):
        return self._choices[obj]

    def to_internal_value(self, data):
        try:
            return list(self._choices.keys())[list(self._choices.values()).index(data)]
        except ValueError:
            raise serializers.ValidationError("选项值只可为：%s" % '; '.join(
                [str(i) for i in self._choices.values()]))


class CheckerRuleSerializer(serializers.ModelSerializer):
    """工具规则序列化，用户loadcheckers时使用
    """
    labels = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Label.objects.all())
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    severity = ChoicesField(choices=models.CheckRule.SEVERITY_ENG_CHOICES)
    category = ChoicesField(choices=models.CheckRule.CATEGORY_ENG_CHOICES)
    description = serializers.CharField(source="checkruledesc.desc", allow_blank=True, allow_null=True)
    custom = serializers.BooleanField(default=True)
    disable = serializers.BooleanField(default=False)

    class Meta:
        model = models.CheckRule
        fields = [
            "real_name", "display_name", "severity", "category", "rule_title",
            "rule_params", "custom", "languages", "solution", "owner",
            "labels", "description", "disable"
        ]


class CheckerToolLibMapSerializer(serializers.ModelSerializer):
    """工具依赖映射详情序列化
    """

    name = serializers.CharField(source="toollib.name")
    source = serializers.CharField(source="toollib.lib_key")

    def validate(self, attrs):
        name = attrs["toollib"]["name"]
        lib_key = attrs["toollib"]["lib_key"]
        try:
            attrs["toollib"] = models.ToolLib.objects.get(name=name, lib_key=lib_key)
            return attrs
        except models.ToolLib.DoesNotExist:
            raise serializers.ValidationError("指定工具依赖[%s - %s]不存在" % (name, lib_key))

    class Meta:
        model = models.ToolLibMap
        fields = ["name", "source"]


class CheckerSchemeSerializer(serializers.ModelSerializer):
    """工具依赖方案序列化，用户loadcheckers时使用
    """
    tool_libs = CheckerToolLibMapSerializer(many=True, source="toollibmap")

    class Meta:
        model = models.ToolLibScheme
        fields = ["condition", "tool_libs", "scheme_os", "default_flag"]


class CheckerSerializer(serializers.ModelSerializer):
    """工具序列化，用户loadcheckers时使用
    """
    libscheme_set = CheckerSchemeSerializer(many=True, source="libscheme", required=False)
    checkrule_set = CheckerRuleSerializer(many=True)
    task_processes = serializers.SlugRelatedField(slug_field='name', many=True, queryset=models.Process.objects.all())
    scan_app = serializers.SlugRelatedField(slug_field='name', queryset=models.ScanApp.objects.all())
    open_user = serializers.BooleanField(required=False)
    open_saas = serializers.BooleanField(required=False)

    def check_use_toollib_perm(self, toollib, checktool=None):
        """校验工具是否具有此依赖权限
        1. loadlibs脚本执行时，平台生成的工具必须使用公共依赖
        2. 接口执行时，OA接口也仅能使用公共依赖，体验接口可根据org_sid
        """
        if CheckToolManager.check_use_toollib_perm(checktool, toollib):
            return True
        # 兼容体验版，当checktool为None时，校验org_sid和依赖的lib_key
        view = self.context.get("view")
        if view.kwargs.get("org_sid") == toollib.lib_key.split("org_")[-1]:
            return True
        return False

    def validate_name(self, name):
        if self.instance:  # 更新操作
            if self.instance.name != name:  # 更新工具不一致
                raise serializers.ValidationError("工具名称name不能改变")
        elif models.CheckTool.objects.filter(name=name).exists():  # 创建操作，校验是否已存在工具
            raise serializers.ValidationError("该工具已存在")
        return name

    def validate_libscheme_set(self, libscheme_set):
        for libscheme in libscheme_set:
            toollibmap_set = libscheme.get("toollibmap")
            for libmap in toollibmap_set:
                toollib = libmap.get("toollib")
                if not self.check_use_toollib_perm(toollib, self.instance):
                    raise serializers.ValidationError("没有依赖%s权限" % toollib.name)
        return libscheme_set

    def validate(self, attrs):
        # 用于排除页面操作open_user，open_saas字段
        user = self.context.get("user", None)
        is_local_script = self.context.get("is_local_script", False)
        if not is_local_script and not (user and user.is_superuser):
            # 页面操作非超管不传递open_user， open_saas字段
            attrs.pop("open_user", False)
            attrs.pop("open_saas", False)
        return attrs

    class Meta:
        model = models.CheckTool
        fields = [
            "name", "display_name", "description", "license", "libscheme_set",
            "task_processes", "scan_app", "scm_url", "run_cmd", "envs", "build_flag",
            "checkrule_set", "open_user", "open_saas", "virtual_name", "show_display_name"
        ]


class CheckPackageSerializer(CDBaseModelSerializer):
    """规则包配置序列化
    """
    labels = serializers.SlugRelatedField(queryset=models.Label.objects.all(), slug_field='name', many=True,
                                          help_text="规则包标签")
    languages = serializers.SlugRelatedField(queryset=models.Language.objects.all(), slug_field="name", many=True,
                                             help_text="适用语言")
    checktool = CheckToolSimpleSerializer(many=True, read_only=True, help_text="关联工具")
    selected = serializers.SerializerMethodField()  # 用于判断规则集是否已经存在该规则包
    checkrule_count = serializers.SerializerMethodField()  # 规则包包含的规则数量
    custom_checkrule_count = serializers.SerializerMethodField()

    def get_selected(self, checkpackage):
        """用于判断规则集是否已经存在该规则包
        """
        view = self.context.get("view")
        if view:
            checkprofile_id = view.kwargs.get("checkprofile_id")
            checkprofile = models.CheckProfile.objects.filter(id=checkprofile_id).first()
            if checkprofile:
                pkg_ids = checkprofile.checkpackages.all().values_list("id", flat=True)
                if checkpackage.id in pkg_ids:
                    return True
        return False

    def get_custom_checkrule_count(self, checkpackage):
        """用于规则配置获取官方规则包自定义规则数量
        """
        view = self.context.get("view")
        checkprofile_id = view.kwargs.get("checkprofile_id")
        # 规则集-规则包详情接口使用。获取对官方规则包的自定义规则数量
        if checkprofile_id and checkpackage.package_type == models.CheckPackage.PackageTypeEnum.OFFICIAL:
            checkprofile = models.CheckProfile.objects.filter(id=checkprofile_id).first()
            if checkprofile:
                checkrules = checkpackage.checkrule.all()
                return checkprofile.custom_checkpackage.checkrule.filter(id__in=checkrules).count()
        return None

    def get_checkrule_count(self, checkpackage):
        """获取规则包中包含多少规则数量
        """
        return checkpackage.checkrule.all().count()

    def _create_or_update(self, validated_data, instance=None):
        # 自定义规则包无需该通过页面create or update，仅官方规则包需要
        request = self.context.get("request")
        user = request.user if request else None
        name = validated_data.pop("name")
        checkpackage = core.CheckPackageManager.create_or_update(name, models.CheckPackage.PackageTypeEnum.OFFICIAL,
                                                                 user, instance=instance, **validated_data)
        return checkpackage

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.CheckPackage
        exclude = ["checkrule"]
        read_only_fields = ["revision", "package_type", "disable"]


class CheckPackageRuleUpdateSerializer(serializers.Serializer):
    """严重级别、规则参数、状态序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    severity = serializers.ChoiceField(choices=models.CheckRule.SEVERITY_CHOICES, help_text="严重级别")
    rule_params = serializers.CharField(help_text="规则参数", allow_null=True, allow_blank=True)
    state = serializers.ChoiceField(choices=models.PackageMap.STATE_CHOICES, help_text="状态，1生效中，2已屏蔽")


class CheckPackageRuleSeverityUpdateSerializer(serializers.Serializer):
    """规则包规则严重级别更新序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    severity = serializers.ChoiceField(choices=models.CheckRule.SEVERITY_CHOICES, help_text="严重级别")


class CheckPackageRuleStateUpdateSerializer(serializers.Serializer):
    """规则包规则状态更新序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    state = serializers.ChoiceField(choices=models.PackageMap.STATE_CHOICES, help_text="状态，1生效中，2已屏蔽")
    remark = serializers.CharField(allow_null=True, allow_blank=True, required=False, help_text="remark")


class CheckPackageRuleDeleteSerializer(serializers.Serializer):
    """规则包规则删除序列化
    """
    packagemaps = serializers.PrimaryKeyRelatedField(queryset=models.PackageMap.objects.all(), many=True,
                                                     help_text="规则包规则列表")
    reason = serializers.CharField(max_length=128, help_text="删除原因")


class CheckProfileDetailSerializer(CDBaseModelSerializer):
    """规则集序列化
    """
    checkpackages = CheckPackageSerializer(many=True, help_text="规则包列表", allow_null=True)

    class Meta:
        model = models.CheckProfile
        fields = ["id", 'custom_checkpackage', 'checkpackages']
        read_only_fields = ["custom_checkpackage"]


class CheckProfilePackageAddSerializer(serializers.Serializer):
    """规则集添加规则包序列化
    """
    checkpackages = serializers.PrimaryKeyRelatedField(
        queryset=models.CheckPackage.objects.filter(package_type=models.CheckPackage.PackageTypeEnum.OFFICIAL),
        many=True)


class PackageMapJsonSerializer(serializers.ModelSerializer):
    """规则包json序列化
    """
    checktool = serializers.CharField(source="checktool.name")
    checkrule = serializers.CharField(source="checkrule.real_name")
    checkrule_display_name = serializers.CharField(source="checkrule.display_name", read_only=True)
    checktool_display_name = serializers.CharField(source="checktool.display_name", read_only=True)
    checkrule_category = ChoicesField(choices=models.CheckRule.CATEGORY_ENG_CHOICES, source="checkrule.category",
                                      read_only=True)
    severity = ChoicesField(choices=models.CheckRule.SEVERITY_ENG_CHOICES)
    state = ChoicesField(choices=models.PackageMap.STATE_ENG_CHOICES)

    def validate(self, attrs):
        tool_name = attrs["checktool"]["name"]
        rule_name = attrs["checkrule"]["real_name"]
        try:
            attrs["checktool"] = models.CheckTool.objects.get(name=tool_name)
            attrs["checkrule"] = models.CheckRule.objects.get(real_name=rule_name, checktool=attrs["checktool"])
            return attrs
        except (models.CheckRule.DoesNotExist, models.CheckTool.DoesNotExist):
            raise serializers.ValidationError("指定工具规则[%s/ %s]不存在" % (tool_name, rule_name))

    class Meta:
        model = models.PackageMap
        fields = ["checktool", "checkrule", "severity", "rule_params", "state", "checkrule_category",
                  "checkrule_display_name", "checktool_display_name"]


class CheckPackageJsonSerializer(serializers.ModelSerializer):
    """获取/创建规则包序列化
    """
    labels = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Label.objects.all())
    checkrule_set = PackageMapJsonSerializer(many=True, source="get_package_maps")
    package_type = ChoicesField(choices=models.CheckPackage.PACKAGETYPE_ENG_CHOICES, required=False,
                                default=models.CheckPackage.PackageTypeEnum.OFFICIAL)
    languages = serializers.SlugRelatedField(slug_field="name", many=True, queryset=models.Language.objects.all())
    open_saas = serializers.BooleanField(required=False)
    status = serializers.ChoiceField(choices=models.CheckPackage.STATUS_CHOICES,
                                     default=models.CheckPackage.StatusEnum.RUNNING,
                                     write_only=True, required=False)

    def validate_name(self, name):
        if self.instance:  # 更新操作
            if self.instance.name != name:  # 更新规则包名称不一致
                raise serializers.ValidationError("规则包名称name不能改变")
        elif models.CheckPackage.objects.filter(name=name).exists():  # 创建操作
            raise serializers.ValidationError("该规则包已存在")
        return name

    def create(self, validated_data):
        checkrules_data = validated_data.pop('get_package_maps')
        checkpackage = super().create(validated_data)
        core.CheckPackageManager.save_pms_by_script(checkpackage, checkrules_data)
        return checkpackage

    def update(self, checkpackage, validated_data):
        checkrules_data = validated_data.pop('get_package_maps')
        core.CheckPackageManager.save_pms_by_script(checkpackage, checkrules_data)
        return super().update(checkpackage, validated_data)

    class Meta:
        model = models.CheckPackage
        fields = ["name", "description", "revision", "package_type", "languages",
                  "labels", "checkrule_set", "open_saas", "envs", "status"]


class ToolLibEditSerializer(CDBaseModelSerializer):
    """工具依赖编辑序列化，用于创建、更新工具依赖序列化
    """

    scm_auth = ScmAuthCreateSerializer(write_only=True, help_text="关联授权信息", allow_null=True, required=False)
    envs = serializers.JSONField()

    def get_user(self):
        request = self.context.get("request")
        user = request.user if request else None
        # 从脚本执行
        if self.context.get("is_local_script", False) and self.context.get("user"):
            user = self.context.get("user")
        return user

    def validate_lib_type(self, lib_type):
        """非超管仅能创建私有依赖，超管可选择
        """
        user = self.get_user()
        if user and user.is_superuser:
            return lib_type
        return models.ToolLib.LibTypeEnum.PRIVATE

    def validate(self, attrs):
        scm_type = attrs.get("scm_type")
        scm_url = attrs.get("scm_url")
        # 工具依赖地址为link类型，则跳过scm_url鉴权
        if scm_type == models.ToolLib.ScmTypeEnum.LINK:
            return super().validate(attrs)
        # 对scm_url执行凭证鉴权处理
        user = self.get_user()
        scm_auth = attrs.get("scm_auth")
        if not scm_auth:
            raise serializers.ValidationError({"scm_auth": "凭证为必填项"})
        auth_type = scm_auth.get("auth_type")
        if auth_type == models.ScmAuth.ScmAuthTypeEnum.PASSWORD:
            scm_account = scm_auth.get("scm_account")
            if not scm_account or scm_account.user != user:
                raise serializers.ValidationError({"scm_auth": "请选择有效HTTP凭证"})
            credential_info = scm_account.credential_info
        elif auth_type == models.ScmAuth.ScmAuthTypeEnum.SSHTOKEN:
            scm_ssh = scm_auth.get("scm_ssh")
            if not scm_ssh or scm_ssh.user != user:
                raise serializers.ValidationError({"scm_auth": "请选择有效SSH凭证"})
            credential_info = scm_ssh.credential_info
        else:
            raise serializers.ValidationError({"auth_type": ["不支持%s鉴权方式" % auth_type]})
            # 校验
        ScmAuthManager.check_scm_url_credential(scm_type, scm_url, credential_info)
        return super().validate(attrs)

    def _create_or_update(self, validated_data, instance=None):
        user = self.get_user()
        name = validated_data.pop("name")
        scm_auth = validated_data.pop("scm_auth", None)
        instance, _ = ToolLibManager.create_or_update(name, user, instance=instance, **validated_data)
        # 保存凭证信息
        if validated_data.get("scm_type") != models.ToolLib.ScmTypeEnum.LINK and scm_auth:
            ScmAuthManager.create_toollib_auth(
                instance, user, scm_auth_type=scm_auth.get("auth_type"),
                scm_account=scm_auth.get("scm_account"),
                scm_ssh_info=scm_auth.get("scm_ssh")
            )
        return instance

    def create(self, validated_data):
        return self._create_or_update(validated_data)

    def update(self, instance, validated_data):
        return self._create_or_update(validated_data, instance)

    class Meta:
        model = models.ToolLib
        exclude = ["lib_key"]
