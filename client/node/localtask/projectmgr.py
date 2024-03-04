# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
ProjectMgr
"""

import json
import logging
import sys

from node.localtask.localreport import LocalReport
from node.localtask.schememgr import SchemeManager
from node.localtask.urlmgr import UrlMgr
from node.localtask.scanmodule import ScanModule
from node.localtask.langmgr import LanguageManager
from util import errcode
from util.exceptions import NodeError, ResfulApiError
from util.scmurlmgr import BaseScmUrlMgr, ScmUrlMgr
from util.logutil import LogPrinter

logger = logging.getLogger(__name__)


class ProjectMgr(object):
    def __init__(self, scan_plan, scheme_template_ids, scheme_templates, languages,
                 dog_server, org_sid, team_name, source_dir, include_paths, exclude_paths,
                 proj_id, scm_info, report_file, admins, scm_auth_info, front_end_url,
                 labels, machine_tag, ref_scheme_id, proj_env, create_from, enable_module):
        self._repo_id = None
        self._scan_plan = scan_plan
        self._scheme_template_ids = scheme_template_ids
        self._scheme_templates = scheme_templates
        self._languages = languages
        self._dog_server = dog_server
        self._org_sid = org_sid
        self._team_name = team_name
        self._source_dir = source_dir
        self._include_paths = include_paths
        self._exclude_paths = exclude_paths
        self._proj_id = proj_id
        self._scm_info = scm_info
        self._report_file = report_file
        self._admins = admins
        self._scm_auth_info = scm_auth_info
        self._front_end_url = front_end_url
        self._labels = labels
        self._machine_tag = machine_tag
        self._ref_scheme_id = ref_scheme_id
        self._proj_env = proj_env
        self._create_from = create_from
        self._enable_module = enable_module

    def __check_project_exist(self, branch, scheme_name, scan_path):
        """
        判断项目是否已存在
        :return:
        """
        # 向serer查询是否已创建项目
        try:
            proj_info_list = self._dog_server.get_proj_info(branch=branch, scan_scheme=scheme_name,
                                                            repo_id=self._repo_id, org_sid=self._org_sid,
                                                            team_name=self._team_name, scan_path=scan_path)
        except ResfulApiError as err:
            logger.error("获取项目ID失败,退出!\n%s", err.msg)
            sys.exit(-1)

        if proj_info_list:
            if len(proj_info_list) == 1:
                return proj_info_list[0]
            else:
                proj_info_list_str = json.dumps(proj_info_list, indent=2, ensure_ascii=False)
                err_msg = f"该仓库(id: {self._repo_id})下的{branch}分支, 使用 {scheme_name} 分析方案的项目有多个," \
                          f"请联系代码分析管理员排查原因.\n{proj_info_list_str}"
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=err_msg)
        else:
            return None

    def __check_and_create_repo(self, repo_url):
        is_existed, repo_id = self._dog_server.is_repo_existed(repo_url, self._org_sid, self._team_name)
        if is_existed:
            return repo_id
        else:
            repo_info = {
                "scm_url": repo_url,
                "scm_type": self._scm_info.scm_type,
                "created_from": "tca_client",
                "admins": self._admins,
                "users": self._admins
            }
            repo_id = self._dog_server.create_repo(repo_info, self._org_sid, self._team_name)
            return repo_id

    def __check_no_language_exit(self):
        """
        自动识别语言后，发现项目不包含支持的语言代码文件，直接跳过，正常退出
        :return:
        """
        if not self._languages:
            scan_result = {
                "status": "success",
                "error_code": errcode.OK,
                "url": "",
                "text": "skip",
                "description": "Source dir contains no code, skip.",
                "scan_report": {}
            }
            LocalReport.output_report(scan_result, self._report_file)
            sys.exit(0)  # 正常退出

    def _check_scheme(self, repo_schemes):
        """判断分析方案是否存在"""
        url_mgr = UrlMgr(self._front_end_url, repo_id=self._repo_id, org_sid=self._org_sid, team_name=self._team_name)
        is_scheme_existed, scheme_params = SchemeManager.check_and_create_scheme(self._repo_id,
                                                                                 repo_schemes,
                                                                                 self._scan_plan,
                                                                                 self._ref_scheme_id,
                                                                                 self._scheme_template_ids,
                                                                                 self._scheme_templates,
                                                                                 self._languages,
                                                                                 url_mgr,
                                                                                 self._dog_server,
                                                                                 self._org_sid,
                                                                                 self._team_name,
                                                                                 self._source_dir,
                                                                                 self._include_paths,
                                                                                 self._exclude_paths,
                                                                                 self._proj_id)
        if is_scheme_existed is False and scheme_params == "EmptyLanguage":
            # 项目不包含语言，直接退出
            self.__check_no_language_exit()

        scheme_name = scheme_params.get("name")

        return scheme_name, is_scheme_existed

    def check_and_create_proj(self, scan_path):
        """
        根据代码库url查询是否有创建项目,如果没有,新建项目
        :return:
        """
        # 判断如果本地url是ssh鉴权方式,转换为http格式(因为server端暂不支持ssh格式的url)
        ssh_scm_type = BaseScmUrlMgr.check_ssh_scm_type(self._scm_info.scm_url)
        # 转换成http格式的url
        if ssh_scm_type:
            scm_url_mgr = ScmUrlMgr(ssh_scm_type).get_scm_url_mgr()
            format_scm_url = scm_url_mgr.ssh_to_http(self._scm_info.scm_url)
            format_repo_url = scm_url_mgr.ssh_to_http(self._scm_info.scm_url)  # 仓库地址
        else:
            format_scm_url = self._scm_info.scm_url
            format_repo_url = self._scm_info.scm_url

        # 没有管理员的情况下,如果有传scm用户名,使用该用户作为管理员
        if not self._admins:
            if self._scm_auth_info.username:
                self._admins = [self._scm_auth_info.username]

        # 1. 判断代码库，如果不存在，先关联
        self._repo_id = self.__check_and_create_repo(format_repo_url)
        # 获取仓库下的分析方案列表
        repo_schemes = self._dog_server.get_repo_schemes(self._repo_id, self._org_sid, self._team_name)

        # 2. 判断分析方案是否存在
        scheme_name, is_scheme_existed = self._check_scheme(repo_schemes)

        # 3. 判断项目是否存在
        proj_info = self.__check_project_exist(self._scm_info.branch, scheme_name, scan_path)
        if proj_info:
            self._proj_id = proj_info["id"]
            is_scheme_existed = True
            scheme_name = proj_info["scan_scheme"]["name"]
        else:
            self._proj_id = None

        if self._proj_id:  # 已有项目,复用
            LogPrinter.info(f"Use the already existed project(id: {self._proj_id}).")
        else:  # 没有项目,需要新建项目
            # 分析方案已存在，直接复用，不需要语言参数
            # 指定了参照扫描方案ID，可以复制该扫描方案，不需要语言参数
            if is_scheme_existed or self._languages or self._ref_scheme_id:
                pass
            else:
                # 补充语言参数
                self._languages = LanguageManager.auto_identify_languages(self._source_dir, self._include_paths,
                                                                          self._exclude_paths, self._dog_server,
                                                                          self._repo_id, self._proj_id, self._org_sid,
                                                                          self._team_name)
                self.__check_no_language_exit()

            if not scan_path:
                scan_path = '/'
            if self._ref_scheme_id:
                proj_info = {
                    "scm_type": self._scm_info.scm_type,
                    "scm_url": format_scm_url,
                    "scheme_name": scheme_name,
                    "refer_scheme_id": self._ref_scheme_id,
                    "created_from": self._create_from,
                    "admins": self._admins,
                    "scan_path": scan_path
                }
            else:
                enable_module_setting = ScanModule.get_module_setting(self._enable_module)
                proj_info = {
                    "scm_type": self._scm_info.scm_type,
                    "scm_url": format_scm_url,
                    "scm_username": None,
                    "scm_password": None,
                    "languages": self._languages,
                    "labels": self._labels or [],
                    "envs": self._proj_env,
                    "admins": self._admins,
                    "users": [],
                    "tag": self._machine_tag,
                    "scheme_name": scheme_name,
                    "scheme_templates": self._scheme_templates,
                    "lint_enabled": enable_module_setting["lint"],
                    "cc_scan_enabled": enable_module_setting["cc"],
                    "dup_scan_enabled": enable_module_setting["dup"],
                    "cloc_scan_enabled": enable_module_setting["cloc"],
                    "created_from": self._create_from,
                    "scan_path": scan_path
                }

            logger.info("开始自动创建项目...")

            try:
                with open("create_proj.json", "w") as wf:
                    json.dump(proj_info, wf, indent=2)
                proj_server_info = self._dog_server.create_proj(proj_info, self._org_sid, self._team_name)
            except ResfulApiError as error:
                err_msg = "创建项目失败!\n%s" % error.msg
                err_msg += "请联系codedog管理员确认语言对应的规则集是否存在!"
                raise ResfulApiError(err_msg)
            logger.info("创建项目成功.")

            self._proj_id = proj_server_info["project_id"]
        return self._repo_id, self._proj_id
