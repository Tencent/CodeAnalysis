# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
在上报结果中加入变更文件信息， 用于服务器收集增量信息

"""


import logging

from task.basic.datahandler.handlerbase import HandlerBase
from task.basic.datahandler.issueignore import COMMENTIGNORE
from task.scmmgr import SCMMgr

logger = logging.getLogger(__name__)

NO_DIFFINFO = 0
NORMAL_DIFFINFO = 1
CCN_DIFFINFO = 2
DUPLICATE_DIFFINFO = 3


class PackDiffInfo(HandlerBase):
    def run(self, params):
        if self.handle_type == NO_DIFFINFO:
            return params
        elif self.handle_type == NORMAL_DIFFINFO:
            return self._normal_diff_info(params)
        elif self.handle_type == CCN_DIFFINFO:
            return self._ccn_diff_info(params)
        elif self.handle_type == DUPLICATE_DIFFINFO:
            return self._duplicate_diff_info(params)
        return params

    def _normal_diff_info(self, params):
        """
        对工具的扫描结果进行diff信息插入， 便于server端进行关单等操作
        :param params:
        :return:
        """
        if params.get("incr_scan", False):
            issues = params["result"]
            diffs = SCMMgr(params).get_scm_diff()

            # diff 存到一个字典里,增加 in_issues 字段来标记 path 是否已经在 issues 里面
            diff_dict = {}
            for diff in diffs:
                diff_dict[diff.path] = {"change_type": diff.state, "in_issues": False}

            # 在每个 issue 中增加 change_type 信息
            for issue in issues:
                path = issue["path"]
                if path in diff_dict:
                    issue["change_type"] = diff_dict[path]["change_type"]
                    diff_dict[path]["in_issues"] = True
                else:
                    issue["change_type"] = None

            # 为了关单,没有检查出问题的文件,如果 diff 状态是 del 和 mod,也需要把变更信息添加到issues中
            for path, diff_info in diff_dict.items():
                if not diff_info["in_issues"]:
                    if diff_info["change_type"] == "del":
                        issues.append({"path": path, "change_type": "del"})
                    elif diff_info["change_type"] == "mod":
                        issues.append({"path": path, "change_type": "mod", "issues": []})

            params["result"] = issues
        return params

    def _ccn_diff_info(self, params):
        """
        对工具的扫描结果进行diff信息插入， 便于server端进行关单等操作
        全量不做处理，故没有change_type
        :param params:
        :return:
        """
        logger.info("start: insert issues with ccn diff info.")
        fileissues = params["result"]["detail"]
        summary = params["result"]["summary"]

        if params.get("incr_scan", False):
            scm_client = SCMMgr(params).get_new_scm_client()

            # 修改diff逻辑，优先与起始版本号进行diff，若没有起始版本号，则与上一版本号做diff
            last_revision = (
                params.get("scm_initial_last_revision")
                if params.get("scm_initial_last_revision")
                else params.get("scm_last_revision")
            )
            logger.info(f"对比版本号是: {last_revision}")
            diffs = SCMMgr(params).get_scm_diff(last_revision=last_revision)
            now_revision = params["scm_revision"]
            # last_revision = params['scm_last_revision']

            # diff 存到一个字典里,增加 in_issues 字段来标记 path 是否已经在 issues 里面
            diff_dict = {}
            for diff in diffs:
                try:
                    diff_dict[diff.path] = {"change_type": diff.state, "in_issues": False}
                except Exception as e:
                    logger.error(f"{diff} error: {e}")
                    raise

            # 在每个 issue 中增加 change_type 信息
            for fileissue in fileissues:
                path = fileissue["path"]
                if path in diff_dict:
                    fileissue["change_type"] = diff_dict[path]["change_type"]
                    diff_dict[path]["in_issues"] = True

                    # 获取该文件其中每个issue的代码行区间的change_type
                    logger.debug(
                        "file_path: %s, last_revision: %s, now_revision: %s", path, last_revision, now_revision
                    )
                    diff_info = scm_client.diff_lines(path, last_revision, now_revision)
                    # 需要遍历file里面的issue
                    for issue in fileissue.get("issues", []):
                        change_type = SCMMgr(params).get_block_change_type(
                            diff_info, issue["start_line_no"], issue["end_line_no"]
                        )
                        issue["change_type"] = change_type

                        for key in ("default", "custom"):
                            if key not in summary:
                                continue
                            # 统计差异超标函数个数
                            if (
                                issue["ccn"] > summary[key]["min_ccn"]
                                and change_type
                                and issue.get("resolution") != COMMENTIGNORE
                            ):
                                summary[key]["diff_over_cc_func_count"] += 1
                else:
                    # 没有变化的文件，change_type为None
                    fileissue["change_type"] = None
                    for issue in fileissue.get("issues", []):
                        issue["change_type"] = None

            # 为了关单,没有检查出问题的文件,如果 diff 状态是 del 和 mod,也需要把变更信息添加到issues中
            self._diff_info_for_other_files(fileissues, diff_dict)

        # 过滤小于custom_min_ccn的issue
        if "custom" in summary and summary["custom"]["min_ccn"] > summary["default"]["min_ccn"]:
            custom_min_ccn = summary["custom"]["min_ccn"]
            for fileissue in fileissues:
                fileissue["issues"] = [issue for issue in fileissue.get("issues", []) if issue["ccn"] > custom_min_ccn]

        params["result"]["detail"] = fileissues
        params["result"]["summary"] = summary

        logger.info("finished: insert issues with ccn diff info.")
        return params

    def _diff_info_for_other_files(self, fileissues, diff_dict, issue_tag="issues"):
        """
        为了关单,没有检查出问题的文件,如果 diff 状态是 del 和 mod,也需要把变更信息添加到issues中
        """
        for path, diff_info in diff_dict.items():
            if not diff_info["in_issues"]:
                if diff_info["change_type"] == "del":
                    fileissues.append({"path": path, "change_type": "del"})
                elif diff_info["change_type"] == "mod":
                    fileissues.append({"path": path, "change_type": "mod", issue_tag: []})

    def _duplicate_diff_info(self, params):
        """
        对工具的扫描结果进行diff信息插入， 便于server端进行关单等操作
        全量不做处理，故没有change_type
        :param params:
        :return:
        """
        logger.info("start: insert issues with diff info.")
        fileissues = params["result"]

        # 定义的文件重复率风险指标，文件重复率越高风险就越大. 这里分为4个区间
        # 低风险：0%到dup_min_midd_rate 这个不用上传给Server
        # 中风险：dup_min_midd_rate到dup_min_high_rate
        # 高风险：dup_min_high_rate到dup_min_exhi_rate
        # 极高风险：dup_min_exhi_rate到100%

        DEFAULT_DUP_MIN_MIDD_RATE = params["DEFAULT_DUP_MIN_MIDD_RATE"]
        DEFAULT_DUP_MIN_HIGH_RATE = params["DEFAULT_DUP_MIN_HIGH_RATE"]
        DEFAULT_DUP_MIN_EXHI_RATE = params["DEFAULT_DUP_MIN_EXHI_RATE"]

        custom_dup_min_midd_rate = params.get("dup_min_midd_rate", DEFAULT_DUP_MIN_MIDD_RATE * 100) / 100
        custom_dup_min_high_rate = params.get("dup_min_high_rate", DEFAULT_DUP_MIN_HIGH_RATE * 100) / 100
        custom_dup_min_exhi_rate = params.get("dup_min_exhi_rate", DEFAULT_DUP_MIN_EXHI_RATE * 100) / 100
        is_custom = (
            False
            if custom_dup_min_midd_rate == DEFAULT_DUP_MIN_MIDD_RATE
            and custom_dup_min_high_rate == DEFAULT_DUP_MIN_HIGH_RATE
            and custom_dup_min_exhi_rate == DEFAULT_DUP_MIN_EXHI_RATE
            else True
        )

        # 统计项目数据
        project_datas = [
            {
                "exhi_risk": {"range": (DEFAULT_DUP_MIN_EXHI_RATE, 1), "file_count": 0, "diff": {"diff_file_count": 0}},
                "high_risk": {
                    "range": (DEFAULT_DUP_MIN_HIGH_RATE, DEFAULT_DUP_MIN_EXHI_RATE),
                    "file_count": 0,
                    "diff": {"diff_file_count": 0},
                },
                "midd_risk": {
                    "range": (DEFAULT_DUP_MIN_MIDD_RATE, DEFAULT_DUP_MIN_HIGH_RATE),
                    "file_count": 0,
                    "diff": {"diff_file_count": 0},
                },
                "low_risk": {"range": (0, DEFAULT_DUP_MIN_MIDD_RATE), "file_count": 0, "diff": {"diff_file_count": 0}},
            },
            {
                "exhi_risk": {"range": (custom_dup_min_exhi_rate, 1), "file_count": 0, "diff": {"diff_file_count": 0}},
                "high_risk": {
                    "range": (custom_dup_min_high_rate, custom_dup_min_exhi_rate),
                    "file_count": 0,
                    "diff": {"diff_file_count": 0},
                },
                "midd_risk": {
                    "range": (custom_dup_min_midd_rate, custom_dup_min_high_rate),
                    "file_count": 0,
                    "diff": {"diff_file_count": 0},
                },
                "low_risk": {"range": (0, custom_dup_min_midd_rate), "file_count": 0, "diff": {"diff_file_count": 0}},
            },
        ]

        if params.get("incr_scan", False):
            scm_client = SCMMgr(params).get_new_scm_client()
            diffs = SCMMgr(params).get_scm_diff()
            now_revision = params["scm_revision"]
            last_revision = params["scm_last_revision"]

            # diff 存到一个字典里,增加 in_issues 字段来标记 path 是否已经在 issues 里面
            diff_dict = {}
            for diff in diffs:
                diff_dict[diff.path] = {"change_type": diff.state, "in_issues": False}

            # 在每个 issue 中增加 change_type 信息
            for fileissue in fileissues:
                path = fileissue["path"]
                if path in diff_dict:
                    fileissue["change_type"] = diff_dict[path]["change_type"]
                    diff_dict[path]["in_issues"] = True

                    # 获取该文件其中每个issue的代码行区间的change_type
                    logger.debug(
                        "file_path: %s, last_revision: %s, now_revision: %s", path, last_revision, now_revision
                    )
                    diff_info = scm_client.diff_lines(path, last_revision, now_revision)
                    # 需要遍历file里面的issue
                    for issue in fileissue.get("code_blocks", []):
                        change_type = SCMMgr(params).get_block_change_type(
                            diff_info, issue["start_line_num"], issue["end_line_num"]
                        )
                        issue["change_type"] = change_type
                else:
                    # 没有变化的文件，change_type为None
                    fileissue["change_type"] = None
                    for issue in fileissue.get("code_blocks", []):
                        issue["change_type"] = None

            # 为了关单,没有检查出问题的文件,如果 diff 状态是 del 和 mod,也需要把变更信息添加到issues中
            self._diff_info_for_other_files(fileissues, diff_dict, issue_tag="code_blocks")

        # 统计项目数据
        self.__handle_project_datas(project_datas, fileissues)

        project_duplication_rate = (
            params["PROJECT_DUPLICATION_RATE"]
            if "PROJECT_DUPLICATION_RATE" in params
            else params["PROJECT_DUPLICATION_RATE_LIMITED"]
        )
        project_duplication_line_count = (
            params["PROJECT_DUPLICATION_LINE_COUNT"]
            if "PROJECT_DUPLICATION_LINE_COUNT" in params
            else params["PROJECT_DUPLICATION_LINE_COUNT_LIMITED"]
        )

        params["result"] = {
            "summary": {
                "duplication_rate": "%.2f" % (project_duplication_rate * 100),
                "total_duplicate_line_count": str(project_duplication_line_count),
                "total_line_count": str(params["PROJECT_LINE_COUNT"]),
                "default": project_datas[0],
            },
            "detail": fileissues,
        }
        if is_custom:
            params["result"]["summary"]["custom"] = project_datas[1]

        logger.info("finished: insert issues with diff info.")
        return params

    def __handle_project_datas(self, project_datas, fileissues):
        """
        统计项目数据
        """
        for fileissue in fileissues:
            if not fileissue.get("code_blocks", []):
                continue

            duplicate_rate = float(fileissue["duplicate_rate"]) / 100

            for i in range(len(project_datas)):
                data = project_datas[i]
                for key in data.keys():
                    if data[key]["range"][0] <= duplicate_rate < data[key]["range"][1] or (
                        key == "exhi_risk" and duplicate_rate == 1
                    ):
                        if i == 1:
                            fileissue["risk"] = key.split("_")[0]
                        data[key]["file_count"] += 1
                        if fileissue.get("change_type", None):
                            data[key]["diff"]["diff_file_count"] += 1

    @staticmethod
    def get_tool_handle_type_name():
        return "set_result_pack_diff_info"
