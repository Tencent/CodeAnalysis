# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
在结果中添加文件层级信息，比如language,owners字段
"""

import logging

from task.basic.datahandler.handlerbase import HandlerBase
from task.basic.datahandler.issueignore import COMMENTIGNORE

logger = logging.getLogger(__name__)

NO_ADD_PERSON_INFO = 0
CCN_ADD_PERSON_INFO = 2


class AddPersonInfo(HandlerBase):
    @staticmethod
    def get_tool_handle_type_name():
        return "set_add_person_info"

    def run(self, params):
        if self.handle_type == NO_ADD_PERSON_INFO:
            return params
        elif self.handle_type == CCN_ADD_PERSON_INFO:
            return self.__ccn_add_person_info(params)
        return params

    def __ccn_add_person_info(self, params):
        """
        适用ccn
        :param params:
        :return:
        """
        if not params["result"] or not params["result"]["detail"]:
            return params

        default_min_ccn = 20
        custom_min_ccn = int(params.get("min_ccn", default_min_ccn))
        default_over_person = list()
        custom_over_person = list()
        # 个人维度数据
        person_infos = dict()
        # 聚合数据
        logger.info("Start: add ccn person info...")
        for path_issue in params["result"]["detail"]:
            # logger.info(path_issue["path"])
            is_own = False
            owners = ""
            # 适配owner情况
            if "owners" in path_issue:
                is_own = True
                owners = path_issue["owners"]
            owners = [owner for owner in owners.split(";") if owner]
            self.__init_person_info(owners, person_infos)
            issues = path_issue.get("issues", [])
            for issue in issues:
                if issue.get("resolution") == COMMENTIGNORE:
                    continue
                if is_own:
                    issue_owners = owners
                else:
                    modifier = issue.get("most_weight_modifier")
                    if not modifier:
                        continue
                    if modifier not in person_infos:
                        person_infos[modifier] = {
                            "author": modifier,
                            "author_email": issue.get("most_weight_modifier_email", ""),
                            "over_cc_func_count": 0,
                            "over_cc_sum": 0,
                        }
                    issue_owners = [modifier]
                if issue["ccn"] > default_min_ccn:
                    for owner in issue_owners:
                        if owner not in default_over_person:
                            default_over_person.append(owner)
                if issue["ccn"] <= custom_min_ccn:
                    continue
                for owner in issue_owners:
                    if owner not in custom_over_person:
                        custom_over_person.append(owner)
                    person_infos[owner]["over_cc_func_count"] += 1
                    person_infos[owner]["over_cc_sum"] += issue["ccn"]
        for info in person_infos.values():
            info["over_cc_sum"] = (
                info["over_cc_sum"] - info["over_cc_func_count"] * custom_min_ccn
                if info["over_cc_func_count"] != 0
                else 0
            )
        params["result"]["person"] = list(person_infos.values())

        # 超标人均
        self.__calc_ccn_project(params, default_over_person, custom_over_person)

        logger.info("End: add ccn person info.")

        return params

    def __init_person_info(self, owners, person_infos):
        """
        初始化person info
        """
        for owner in owners:
            if owner and owner not in person_infos:
                person_infos[owner] = {
                    "author": owner,
                    # TODO: 后续增加邮箱
                    "author_email": "",
                    "over_cc_func_count": 0,
                    "over_cc_sum": 0,
                }

    def __calc_ccn_project(self, params, default_over_person, custom_over_person):
        """
        计算超标人均相关数据指标
        """
        params["result"]["summary"]["default"]["over_cc_person_count"] = len(default_over_person)
        params["result"]["summary"]["default"]["over_cc_func_count_over_average"] = (
            params["result"]["summary"]["default"]["over_cc_func_count"] / len(default_over_person)
            if len(default_over_person) != 0
            else 0
        )
        params["result"]["summary"]["default"]["over_cc_sum_over_average"] = (
            params["result"]["summary"]["default"]["over_cc_sum"] / len(default_over_person)
            if len(default_over_person) != 0
            else 0
        )
        if "custom" in params["result"]["summary"]:
            params["result"]["summary"]["custom"]["over_cc_person_count"] = len(custom_over_person)
            params["result"]["summary"]["custom"]["over_cc_func_count_over_average"] = (
                params["result"]["summary"]["custom"]["over_cc_func_count"] / len(custom_over_person)
                if len(custom_over_person) != 0
                else 0
            )
            params["result"]["summary"]["custom"]["over_cc_sum_over_average"] = (
                params["result"]["summary"]["custom"]["over_cc_sum"] / len(custom_over_person)
                if len(custom_over_person) != 0
                else 0
            )
