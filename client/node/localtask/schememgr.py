# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务执行器,只执行本地配置好的项目的扫描
"""
import logging

from node.localtask.urlmgr import UrlMgr
from node.localtask.langmgr import LanguageManager
from util.languagetype import LanguageType
from util.logutil import LogPrinter

logger = logging.getLogger(__name__)


class SchemeManager(object):
    @staticmethod
    def check_scheme_by_name(repo_schemes, scheme_name):
        """根据名称查询分析方案"""
        for scheme in repo_schemes:
            if scheme["name"] == scheme_name:
                return True, scheme

        logger.info("scan plan(%s) not exists!" % scheme_name)
        return False, {"name": scheme_name}

    @staticmethod
    def check_scheme_by_template_ids(repo_schemes, scheme_template_ids):
        """根据scheme_template_ids查询分析方案"""
        for scheme in repo_schemes:
            if scheme["refer_template_ids"] and scheme_template_ids:
                # server保存的refer_template_id是int类型，客户端参数是str类型，对比前需要先转换类型
                tmp_str_ids = [str(int_id) for int_id in scheme["refer_template_ids"]]
                if set(tmp_str_ids) == set(scheme_template_ids):
                    return True, scheme

        logger.info(f"scan plan(refer_template_ids: {scheme_template_ids}) not exists!")
        return False, {}

    @staticmethod
    def check_and_create_scheme(repo_id, repo_schemes, scan_plan, ref_scheme_id, scheme_template_ids, scheme_templates, languages,
                                url_mgr, dog_server, org_sid, team_name, source_dir, include_paths, exclude_paths,
                                proj_id):
        """
        检查并创建分析方案
        :return: <bool>方案是否已存在或被创建，<dict>方案参数（如果返回False, 方案参数只包含方案名name）
        """
        # 指定了分析方案模板id，没有指定方案名称，会使用模板名称作为方案名称
        if not scan_plan and ref_scheme_id:
            ref_scheme = dog_server.get_scheme_by_id(ref_scheme_id, org_sid)
            if ref_scheme:
                scan_plan = ref_scheme.get("name")
                LogPrinter.info(f"use the name of refer scheme(id:{ref_scheme_id}) as scheme name: {scan_plan}")

        # 有传分析方案名称，先通过名称判断，如果存在，直接复用
        if scan_plan:
            is_existed, scheme_params = SchemeManager.check_scheme_by_name(repo_schemes, scan_plan)
            if is_existed:
                scheme_id = scheme_params.get("id")
                scheme_name = scheme_params.get("name")
                scheme_url = url_mgr.get_scheme_url(scheme_id)
                LogPrinter.info(f"scan plan({scheme_name}) already exists: {scheme_url}")
                return True, scheme_params

        # 如果有官方分析方案id，通过id查询和创建分析方案（先忽略名称）
        if scheme_template_ids:
            # LogPrinter.info(f"-----> scheme_template_ids: {scheme_template_ids}")
            is_existed, scheme_params = SchemeManager.check_scheme_by_template_ids(repo_schemes, scheme_template_ids)
            if is_existed:
                scheme_name = scheme_params.get("name")
                scheme_id = scheme_params.get("id")
                scheme_url = url_mgr.get_scheme_url(scheme_id)
                if scan_plan and scheme_name != scan_plan:
                    LogPrinter.info(f"指定的分析方案({scan_plan})不存在，使用官方分析方案模板对应的方案({scheme_name})：{scheme_url}")
                else:
                    LogPrinter.info(f"scan plan({scheme_name}) already exists: {scheme_url}")
                return True, scheme_params
            else:  # 不存在，根据官方分析方案id，创建分析方案
                scheme_info = {
                    "templates": scheme_template_ids,
                    "lintbasesetting": {},
                    "metricsetting": {}
                }
                if scan_plan:  # 有名称，用指定的名称命名新分析方案；否则不传名称，会以官方分析方案模板名称拼接生成名称（如果生成的名称已存在，则采用uuid作为名称）
                    scheme_info["name"] = scan_plan
                # 需要语言参数，先检查语言
                if not languages:
                    languages = LanguageManager.auto_identify_languages(source_dir, include_paths,
                                                                        exclude_paths, dog_server,
                                                                        repo_id, proj_id, org_sid,
                                                                        team_name)
                    if not languages:
                        # 未识别到语言
                        return False, "EmptyLanguage"
                scheme_info["languages"] = languages
                scheme_params = dog_server.create_scheme(repo_id, scheme_info, org_sid, team_name)
                scheme_id = scheme_params.get("id")
                scheme_name = scheme_params.get("name")
                scheme_url = url_mgr.get_scheme_url(scheme_id)
                LogPrinter.info(f"create scan plan({scheme_name}): {scheme_url}")
                return True, scheme_params

        if scan_plan:  # 此时，如果分析方案名称有传参，说明该名称的分析方案不存在
            return False, {"name": scan_plan}
        else:  # 分析方案名称未传参，按需生成名字
            if scheme_templates:  # 有官方分析方案模板,通过官方分析方案模板名称生成分析方案名称
                sorted_scheme_templates = sorted(scheme_templates)
                scheme_name = "_".join(sorted_scheme_templates)
                for scheme in repo_schemes:
                    if scheme["name"] == scheme_name:
                        scheme_url = url_mgr.get_scheme_url(scheme["id"])
                        LogPrinter.info(f"scan plan({scheme_name}) already exists: {scheme_url}")
                        return True, scheme
            else:  # 空字符串时，表示默认方案
                scheme_name = ""
                # 使用默认分析方案，判断默认分析方案是否存在
                for scheme in repo_schemes:
                    if scheme["default_flag"] is True:
                        scheme_name = scheme["name"]
                        scheme_url = url_mgr.get_scheme_url(scheme["id"])
                        LogPrinter.info(f"scan plan({scheme_name}) already exists: {scheme_url}")
                        return True, scheme
            # 仍旧没有找到分析方案，说明方案不存在
            LogPrinter.info(f"当前repo没有默认分析方案。")
            return False, {"name": scheme_name}
