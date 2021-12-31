# -*- coding: utf-8 -*-
"""获取指定工具依赖入库
"""
import json
import logging
import os
from os import walk

# 第三方 import
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

# 项目内 import
from apps.authen.models import ScmAccount
from apps.scan_conf.models import ToolLib
from apps.scan_conf.utils import load_toollib
from util.cdcrypto import encrypt

logger = logging.getLogger(__name__)

SCAN_CONF_COMMANDS_PATH = os.path.join(os.path.dirname(os.path.abspath("__file__")),
                                       "apps", "scan_conf", "management", "commands")


class Command(BaseCommand):
    help = "load toollib"

    def add_arguments(self, parser):
        parser.add_argument("lib_name_list", type=str, nargs="+", help="需要load的工具依赖列表")
        parser.add_argument("-a", "--account", type=str, help="账户")
        parser.add_argument("-p", "--password", type=str, help="密码")
        parser.add_argument("-dirname", "--dirname", type=str, help="load dirname path toollib, default: toollib_json")

    def get_or_create_account(self, account, password, user):
        """获取或创建凭证
        """
        password = encrypt(password, settings.PASSWORD_KEY)
        scm_account = ScmAccount.objects.filter(user=user, scm_username=account, auth_origin_id="Codedog").first()
        created = False
        if not scm_account:
            scm_account = ScmAccount.objects.create(
                user=user,
                scm_username=account,
                scm_password=password,
                auth_origin_id="Codedog"
            )
            created = True
        return scm_account, created

    def handle(self, *args, **options):
        account = options.get("account")
        password = options.get("password")
        # 获取工具依赖目录名称，默认为toollib_json
        dirname = options.get("dirname") or "toollib_json"
        # 获取需要load的工具依赖文件名称
        lib_name_list = options.get("lib_name_list")
        if lib_name_list == ["all"]:
            # load目录下全部的依赖
            filename_list = []
            folder_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname)
            for _, _, filenames in walk(folder_path):
                for filename in filenames:
                    if filename.endswith(".json") and "_new" not in filename:
                        filename_list.append(filename[:-5])
            lib_name_list = filename_list
        # 默认使用CodeDog用户
        codedog, _ = User.objects.get_or_create(username="CodeDog")
        # 执行工具依赖load
        scm_account = None
        failed_names = []
        for lib_name in lib_name_list:
            self.stdout.write("loading toollib [%s] ..." % lib_name)
            try:
                file_path = os.path.join(SCAN_CONF_COMMANDS_PATH, dirname, "%s.json" % lib_name)
                with open(file_path, "r") as fd:
                    toollib_info = json.load(fd)
                # 如果是json数组则只取第一项
                if isinstance(toollib_info, list) and len(toollib_info) > 0:
                    toollib_info = toollib_info[0]
                # 存在非link类型的依赖，则需要凭证
                if toollib_info.get("scm_type") != ToolLib.ScmTypeEnum.LINK and not scm_account:
                    if account and password:
                        scm_account, _ = self.get_or_create_account(account, password, codedog)
                    else:
                        raise Exception("account 或 password 为必传参数")
                if scm_account:
                    toollib_info.update({
                        "scm_auth": {
                            "scm_account": scm_account.id,
                            "auth_type": "password"
                        }
                    })
                # 执行工具依赖load
                toollib = load_toollib(toollib_info, codedog)
            except Exception as e:
                logger.error(e)
                failed_names.append(lib_name)
        # 检查执行完毕
        names = ""
        for lib_name in lib_name_list:
            names = names + lib_name + ";"
        self.stdout.write("Finish load [%s]" % names)
        if failed_names:
            self.stdout.write("ERROR!!! Faided toollibs: [%s]" % " ".join(failed_names))
