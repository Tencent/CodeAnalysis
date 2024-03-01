# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
用于对扫描结果进行过滤
"""

import os
import logging
import copy
import threading

from queue import Queue
from multiprocessing import cpu_count
from util.reporter import Reporter, InfoType
from task.scmmgr import SCMMgr
from util.exceptions import TaskFilterError
from util.pathfilter import FilterPathUtil
from task.basic.datahandler.handlerbase import HandlerBase
from task.basic.datahandler.issueignore import COMMENTIGNORE
from util.scanlang.callback_queue import CallbackQueue
from util.mergelib import MergeUtil
from util.scmurlmgr import GitUrlMgr


logger = logging.getLogger(__name__)

# 筛选器类型
NO_FILTER = 0  # 无
DIFF_FILTER = 1  # 筛选文件不在diff清单之中的
REVISION_FILTER = 2  # 筛选版本号过老的
PATH_FILTER = 3  # 筛选路径不在版本控制库中的与白名单中的
CCN_PATH_FILTER = 4  # 度量专用
CCN_REVISION_FILTER = 5  # 度量专用
NO_VERSION_FILTER = 6  # 筛选路径不在白名单中的


class RevisionFilterType(object):
    """
    revision过滤原因
    """

    NoFilter = 0  # 不需要过滤
    TooOld = 1  # 在起始版本号之前, 过滤
    InCompareBranch = 2  # 在对比分支中已存在, 过滤


class Filter(HandlerBase):
    def run(self, params):
        """

        :param params:
        :return:
        """
        if not self.handle_type:
            raise TaskFilterError("the filter type list is empty!")

        if NO_FILTER in self.handle_type:
            return params

        if not params:
            return params
        # 逐个执行
        Reporter(params).update_task_progress(InfoType.FilterTask)
        if DIFF_FILTER in self.handle_type:
            params = self._diff_filter(params)
        if PATH_FILTER in self.handle_type:
            params = self._path_filter(params)
        if CCN_PATH_FILTER in self.handle_type:
            params = self._ccn_path_filter(params)
        if NO_VERSION_FILTER in self.handle_type:
            params = self._no_version_filter(params)
        return params

    def _diff_filter(self, params):
        """根据diff信息过滤issues,并将diff的change_type添加到结果中

        子仓库处理逻辑：若为非关联git子仓库

        :param params:
        :return:
        """
        logger.info("start: filter issues according to scm diff.")
        fileissues = params["result"]
        if not fileissues:
            return params

        if params.get("incr_scan", False):
            filtered_issues = []
            diffs = SCMMgr(params).get_scm_diff()
            # 1. filter incr_scan files
            diff_files = [diff.path.replace(os.sep, "/") for diff in diffs]

            for item in fileissues:
                path = item["path"]
                if path in diff_files:
                    filtered_issues.append(item)

            params["result"] = filtered_issues

        logger.info("finished: filter issues according to scm diff.")
        # logger.info(params['result'])
        return params

    def _path_filter(self, params):
        """1. 过滤不在版本控制下的文件.
           2. 根据 exclude 和 include 配置过滤path.
           3. 过滤 scm external paths.

        :param params:
        :return:
        """
        logger.info("start: filter issues according to path filter.")

        issues = params["result"]
        params["result"] = self.__common_path_filter(issues, params)
        logger.info("finished: filter issues according to path filter.")
        # logger.info(params['result'])
        return params

    def _ccn_path_filter(self, params):
        """
        针对圈复杂度的数据结构修改
           1. 过滤不在版本控制下的文件.
           2. 根据 exclude 和 include 配置过滤path.
           3. 过滤 scm external paths.

        :param params:
        :return:
        """
        logger.info("start: filter issues according to ccn path filter.")

        issues = params["result"]["detail"]
        params["result"]["detail"] = self.__common_path_filter(issues, params)
        logger.info("finished: filter issues according to ccn path filter.")
        # logger.info(params['result'])
        return params

    def __common_path_filter(self, issues, params):
        """
        通用的路径过滤方法
        :param issues:
        :param params:
        :return:
        """
        # 初始化scm模块
        scm_mgr = SCMMgr(params)

        filter_util = FilterPathUtil(params)
        filtered_issues = []

        # 如果设置了环境变量，可以不过滤unversioned file
        if os.getenv("TCA_UNCOMMITTED_CODE") == "True":
            logger.info("env TCA_UNCOMMITTED_CODE=True, uncommited file will not be filtered.")

        que = Queue()

        def filte_worker():

            while not que.empty():
                fileissue = que.get()
                path = fileissue.get("path", False)
                if not path:
                    que.task_done()
                    continue
                path_format = path.replace(os.sep, "/")

                # 根据include和exclude判断path是否需要过滤
                if filter_util.should_filter_path(path_format):
                    logger.info("match excluded path, ignore. %s", path_format)
                    que.task_done()
                    continue

                # 过滤不在版本控制下的文件
                # 该方法的主要耗时来源
                if not os.getenv("TCA_UNCOMMITTED_CODE") == "True":
                    try:
                        if scm_mgr.check_versioned_file(path_format) is False:
                            logger.info("not versioned path, ignore. %s", path_format)
                            que.task_done()
                            continue
                    except Exception as e:
                        logger.exception("check_versioned_file exception: %s - %s", str(e), path)
                        # 判断异常，当做不过滤处理

                fileissue["path"] = path_format
                filtered_issues.append(fileissue)
                que.task_done()

        thread_num = cpu_count()
        for fileissue in issues:
            que.put(fileissue)
        for _ in range(thread_num):
            t = threading.Thread(target=filte_worker, name="filte_worker")
            t.daemon = True
            t.start()
        que.join()

        return filtered_issues

    def _no_version_filter(self, params):
        """

        :param params:
        :return:
        """
        logger.info("start: filter issues according to path filter.")

        fileissues = params["result"]
        filter_util = FilterPathUtil(params)
        filtered_issues = []

        def __no_version_filter_callback__(fileissue):
            path = fileissue.get("path", False)
            if not path:
                return
            path_format = path.replace(os.sep, "/")

            # 根据include和exclude判断path是否需要过滤
            if filter_util.should_filter_path(path_format):
                logger.info("match excluded path, ignore. %s", path_format)
                return

            fileissue["path"] = path_format
            filtered_issues.append(fileissue)

        callback_queue = CallbackQueue(min_threads=50, max_threads=1000)
        for fileissue in fileissues:
            callback_queue.append(__no_version_filter_callback__, fileissue)
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()

        params["result"] = filtered_issues

        logger.info("finished: filter issues according to path filter.")
        # logger.info(params['result'])
        return params

    @staticmethod
    def get_tool_handle_type_name():
        return "set_filter_type_list"


class PostFilter(HandlerBase):
    def run(self, params):
        """
        后置过滤，主要是在blame后执行过滤
        :param params:
        :return:
        """
        if not self.handle_type:
            raise TaskFilterError("the filter type list is empty!")

        if NO_FILTER in self.handle_type:
            return params

        if not params:
            return params
        # 逐个执行
        Reporter(params).update_task_progress(InfoType.PostFilterTask)
        if REVISION_FILTER in self.handle_type:
            params = self._revision_filter(params)
        if CCN_REVISION_FILTER in self.handle_type:
            params = self._ccn_revision_filter(params)
        return params

    def _revision_filter(self, params):
        """
        根据blame获取到的版本号，过滤较老的问题。
        :param params:
        :return:
        """
        logger.info("start: filter issues according to revision.")
        params["result"] = self._common_revision_filter(params, params["result"])
        logger.info("finished: filter issues according to revision.")
        # logger.info(params['result'])
        return params

    def _ccn_revision_filter(self, params):
        """
        针对圈复杂度数据结构的版本过滤
        :param params:
        :return:
        """
        logger.info("start: filter issues according to revision and log message.")
        params["result"]["detail"] = self._ccn_revision_detail_filter(params, params["result"]["detail"])

        logger.info("finished: filter issues according to revision and log message.")
        # logger.info(params['result'])
        return params

    def _ccn_revision_detail_filter(self, params, fileissues):
        """1. 过滤起始版本号之前的revision
           2. 按需过滤merge revision
           3. 按需根据scm log关键字过滤revision

        :param params:
        :return:
        """
        # 获取代码库的scm实例
        scm_mgr = SCMMgr(params)
        scm_client = scm_mgr.get_scm_client()

        logger.info("__get_revision_status_map...")
        # 判断issues中的revision是否需要过滤,并存到字典中 {revision: status}
        revision_status_map = self.__get_revision_status_map(params, fileissues, scm_client)
        logger.info("__get_revision_status_map done...")

        # 多个分支修改一个文件的时候，把增量恶化计算，放在datahandle的重复单过滤之后
        # 根据 revision_status_map 来处理扫描结果
        incr_scan = params["incr_scan"]

        if not incr_scan:
            logger.info("_common_revision_filter done...")
            return fileissues

        func_maps_dict = params.get("func_maps_dict", dict())
        diff_fileissues = params.get("diff_details", dict())
        for fileissue in fileissues:
            path = fileissue.get("path")
            issues = fileissue.get("issues", [])
            # 进行增量恶化文件计算
            diff_fileissue = diff_fileissues.get(path, dict())
            # 获取对应文件的函数映射表
            func_maps = func_maps_dict.get(path, list())

            # 移除两个版本对应的重复单的方法
            remove_issues = []
            diff_remove_issues = []
            for issue in issues:
                if revision_status_map[issue["revision"]] == RevisionFilterType.TooOld:
                    logger.info(f"Issue revision is not newer than base_revision，should be filtered: {issue}")
                    remove_issues.append(issue)
                elif revision_status_map[issue["revision"]] == RevisionFilterType.InCompareBranch:
                    logger.info(f"MR重复单，过滤: {issue}")
                    issue["resolution"] = 4
                    remove_issues.append(issue)
                else:
                    continue
                # 若旧版中也有这个函数，也要移除
                for func_map in func_maps:
                    if func_map["new"] == issue and func_map["old"] and func_map["old"] not in diff_remove_issues:
                        diff_remove_issues.append(func_map["old"])
            # 删除revision在起始版本前的issue
            for issue in remove_issues:
                fileissue["issues"].remove(issue)
            for issue in diff_remove_issues:
                diff_fileissue["issues"].remove(issue)

            # 重新计算超标圈复杂度个数和超标圈复杂度总数
            temp = self.handle_fileissue(params, fileissue)
            diff_temp = self.handle_fileissue(params, diff_fileissue)

            fileissue["diff_over_cc_func_count"] = temp.get("over_cc_func_count", 0) - diff_temp.get(
                "over_cc_func_count", 0
            )
            fileissue["diff_over_cc_sum"] = temp.get("over_cc_sum", 0) - diff_temp.get("over_cc_sum", 0)
            fileissue["worse_func_count"] = temp.get("worse_func_count", 0)
            fileissue["worse"] = (
                fileissue["diff_over_cc_func_count"] > 0
                or fileissue["diff_over_cc_sum"] > 0
                or fileissue["worse_func_count"] > 0
            )

        logger.info("_common_revision_filter done...")
        return fileissues

    def handle_fileissue(self, params, fileissue):
        """
        更新项目级数据
        :param params:
        :param fileissue:
        :return:
        """
        temp = copy.deepcopy(fileissue)
        default_min_ccn = 20
        custom_min_ccn = int(params.get("min_ccn", default_min_ccn))

        custom_file_over_func_cc = 0
        custom_file_over_cc_func_count = 0
        worse_func_count = 0

        issues = temp.get("issues", [])
        for issue in issues:
            if issue.get("resolution") == COMMENTIGNORE:
                continue
            ccn = int(issue["ccn"])
            if ccn > custom_min_ccn:
                custom_file_over_cc_func_count += 1
                custom_file_over_func_cc += ccn
                # 统计new版本的恶化方法个数
                if "diff_ccn" in issue and int(issue["diff_ccn"]) > 0:
                    worse_func_count += 1
        # 恶化方法个数
        temp["worse_func_count"] = worse_func_count
        # 超标圈复杂度总和
        temp["over_func_cc"] = custom_file_over_func_cc
        # 超标圈复杂度函数个数
        temp["over_cc_func_count"] = custom_file_over_cc_func_count
        # 超标函数平均圈复杂度=超标函数圈复杂度总和/超标圈复杂度函数个数
        temp["over_cc_avg"] = (
            custom_file_over_func_cc / custom_file_over_cc_func_count if custom_file_over_cc_func_count != 0 else 0
        )
        # 超标圈复杂度对比总和=超标圈复杂度总和-(超标圈复杂度个数*min_ccn)
        temp["over_cc_sum"] = custom_file_over_func_cc - (custom_file_over_cc_func_count * custom_min_ccn)
        return temp

    def _common_revision_filter(self, params, fileissues):
        """1. 过滤起始版本号之前的revision
           2. 按需过滤merge revision
           3. 按需根据scm log关键字过滤revision

        :param params:
        :return:
        """
        # 获取代码库的scm实例
        scm_mgr = SCMMgr(params)
        scm_client = scm_mgr.get_scm_client()

        logger.info("__get_revision_status_map...")
        # 判断issues中的revision是否需要过滤,并存到字典中 {revision: status}
        revision_status_map = self.__get_revision_status_map(params, fileissues, scm_client)
        logger.info("__get_revision_status_map done...")
        # 根据 revision_status_map 来处理扫描结果
        for fileissue in fileissues:
            path = fileissue.get("path")
            issues = fileissue.get("issues", [])
            remove_issues = []
            for issue in issues:
                if not issue.get("revision"):  # 先判空，避免revision字段不存在的情况
                    logger.warning(f"no revison, skip. issue: {issue}")
                    continue
                if revision_status_map[issue["revision"]] == RevisionFilterType.TooOld:
                    if os.environ.get("NO_MR_FILTER", None) in {"True", "true"}:
                        continue
                    logger.info(f"issue的revision在start_revision之前，过滤: {issue}")
                    remove_issues.append(issue)
                elif revision_status_map[issue["revision"]] == RevisionFilterType.InCompareBranch:
                    if os.environ.get("NO_MR_FILTER", None) in {"True", "true"}:
                        continue
                    logger.info(f"MR重复单,过滤: {issue}")
                    issue["resolution"] = 4
            # 删除revision在起始版本前的issue
            for issue in remove_issues:
                fileissue["issues"].remove(issue)
        logger.info("_common_revision_filter done...")
        return fileissues

    def __get_mr_branch_first_revision(self, params):
        """获取MR源分支的起始版本号"""
        source_dir = params.get("source_dir")
        # 获取是否过滤合并版本的标记
        ignore_merged_issue = params.get("ignore_merged_issue")
        # 获取合流对比分支
        compare_branch = params.get("ignore_branch_issue")
        if source_dir and ignore_merged_issue and compare_branch:
            # 获取git分支名
            repo_url, branch = GitUrlMgr.split_url(params["scm_url"])
            branch_start_revision, _ = MergeUtil().get_start_revision(source_dir, branch, compare_branch)
            if branch_start_revision:
                # 计算分支起始版本号的前一个提交，打印出来，方便对比查问题
                last_revison_before_branch = MergeUtil().get_git_last_revision(source_dir, branch_start_revision)
                if last_revison_before_branch:
                    logger.info(f"the last revison before branch_start_revision: {last_revison_before_branch}")
                return branch_start_revision
        return None

    def __get_compare_branch_revisions(self, params, scm_client):
        """获取MR对比分支上的所有提交版本号"""
        # 获取是否过滤合并版本的标记
        ignore_merged_issue = params.get("ignore_merged_issue", False)
        # 获取合流对比分支
        compare_branch = params.get("ignore_branch_issue")
        compare_branch_revisions = []
        if params["scm_type"] == "git":
            # 获取git分支名
            repo_url, branch = GitUrlMgr.split_url(params["scm_url"])
            # 如果是合流场景，获取目标分支的所有版本号，供后续过滤用
            if ignore_merged_issue and compare_branch and branch != compare_branch:
                compare_branch_revisions = scm_client.list_revisions("origin/{}".format(compare_branch))
        return compare_branch_revisions

    def __get_revision_status_map(self, params, fileissues, scm_client):
        """收集issues中出现的所有revision,并判断这些revision是否需要过滤

        :param params: 任务参数
        :param fileissues: 扫描结果list
        :param scm_client: 代码库的scm实例
        :return: 版本号是否需要过滤的字典 {revision: status}
        """
        # 获取issues中出现的所有版本号,存到set集合中
        issue_revisions = self.__get_issues_revisions(fileissues)

        # 获取MR源分支的起始版本号
        mr_branch_first_revision = self.__get_mr_branch_first_revision(params)
        # 获取MR对比分支上的所有提交版本号
        compare_branch_revisions = self.__get_compare_branch_revisions(params, scm_client)

        # 标记revision是否需要过滤的字典{revision: status}
        # status取值详见RevisionFilterType
        revision_status_map = {}

        # 判断 revision 是否需要过滤,并记录到 revision_status_map 字典中
        for revision in issue_revisions:
            try:
                # 1. 如果issue版本号小于mr分支起始版本号，过滤掉
                if mr_branch_first_revision and scm_client.revision_lt(revision, mr_branch_first_revision):
                    revision_status_map[revision] = RevisionFilterType.TooOld
                    continue

                # 2. 过滤掉已经在MR目标分支上的版本号
                if compare_branch_revisions:
                    logger.info("check revision: %s" % revision)
                    if revision in compare_branch_revisions:
                        logger.info("match MR revision, filter: %s" % revision)
                        revision_status_map[revision] = RevisionFilterType.InCompareBranch
                        continue
            except Exception as err:
                logger.exception("版本号(%s)判断出现异常,跳过,不过滤.原因可能是该版本号已被删除,可能会导致问题过滤失败." % revision)

            # 如果执行到这里且 revision_status_map[revision]还没标记,说明该revision不需要过滤
            if revision not in revision_status_map:
                revision_status_map[revision] = RevisionFilterType.NoFilter
        return revision_status_map

    def __get_issues_revisions(self, fileissues):
        """获取issues中所有出现的版本号,存到set集合中

        :return:revision的set集合
        """
        # 收集issues中出现的revision号,存到set集合里,确保不重复
        issue_cnt = 0
        issue_revisions = set()

        for fileissue in fileissues:
            issues = fileissue.get("issues", [])
            issue_cnt += len(issues)
            issue_revisions.update([issue["revision"] for issue in issues])
        logger.debug("there are %s revisions need to check", len(issue_revisions))
        logger.debug("there are %s issues", issue_cnt)
        return issue_revisions

    @staticmethod
    def get_tool_handle_type_name():
        return "set_filter_type_list"


if __name__ == "__main__":
    pass
