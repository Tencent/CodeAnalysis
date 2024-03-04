# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""代码度量-codecount新版代码统计

使用 cloc 工具扫描指定目录和参照目录，获取代码行、注释等变更信息，上报到Codedog平台（同时包含增量和全量）
"""

import re
import os
import time
import copy
import shutil
import fnmatch
import collections
import xml.etree.cElementTree as ET

from task.scmmgr import SCMMgr
from task.codemetricmodel import CodeMetricModel
from tool.util.cloccount import ClocCountHandler
from task.basic.datahandler.formater import NO_FORMAT
from task.basic.datahandler.filter import NO_FILTER
from task.basic.datahandler.submodulehandle import NO_SUBMODULE_HANDLE
from task.basic.datahandler.blamer import NO_BLAME
from task.basic.datahandler.issuehash import NO_ISSUE_HASH
from util.logutil import LogPrinter
from util.pathfilter import FilterPathUtil
from task.basic.datahandler.addfileinfo import NO_ADD_FILE_INFO


logger = LogPrinter

# 业务模块数据结构
BusinessItem = collections.namedtuple("BusinessItem", ["name", "path_pattern", "subscribers"])
ClocTuple = collections.namedtuple("ClocTuple", ["code_line_num", "comment_line_num", "blank_line_num",
                                                 "total_line_num", "add_code_line_num", "add_comment_line_num",
                                                 "add_blank_line_num", "add_total_line_num", "mod_code_line_num",
                                                 "mod_comment_line_num", "mod_blank_line_num", "mod_total_line_num",
                                                 "del_code_line_num", "del_comment_line_num", "del_blank_line_num",
                                                 "del_total_line_num"])


class ConfigParseException(Exception):
    """业务配置文件解析异常
    """
    pass


class BusinessConfig(object):
    """业务模块配置
    """
    def __init__(self, core_file=None, file_mon=None, business_infos=None, business_relations=None):
        """初始化函数
        :param core_file: str - corefiles.xml 路径
        :param file_mon: str - filemon.xml 路径
        :param business_infos: dict - 服务端配置的业务模块信息
        """
        self._core_file = core_file
        self._file_mon = file_mon
        self._business_infos = copy.copy(business_infos)
        self._business_relations = copy.copy(business_relations)
        self._total_business= []

    @property
    def business_items(self):
        """业务信息
        :return list - 业务信息
        """
        # 注意：如果服务端设置了业务集合，只计算业务集合，其他的忽略
        if self._business_relations:
            return self.analyze_business_relation()
        if self._total_business:
            return self._total_business
        if self._core_file:
            self._total_business.extend(self.analyze_corefile())
        if self._file_mon:
            self._total_business.extend(self.analyze_filemon())
        if self._business_infos:
            self._total_business.extend(self.analyze_server())
        return self._total_business

    @staticmethod
    def _convert_to_unix_path(path):
        return path.replace('\\', '/')

    @staticmethod
    def _convert_str_to_list(name):
        """将str分割为list
        :param name: str - 名称字符串
        :return: list - 名称列表
        """
        return [item for item in re.split(r"[|,;]", name) if item]

    def analyze_corefile(self):
        """解析corefiles.xml文件
        :return: list - BusinessItem列表
        """
        _business_items = []
        tree = ET.ElementTree(file=self._core_file)
        root = tree.getroot()
        if root.tag != "filelist":
            raise ConfigParseException(u"%s was invalid, because it didn't include <filelist> tag" % self._core_file)
        for child_of_root in root:
            if child_of_root.tag != "file":
                raise ConfigParseException(u"%s was invalid，because it included invalid tag: "
                                           u"<%s>" % (self._core_file, child_of_root.tag))
            business_item = BusinessItem(name="corefiles.xml",
                                         path_pattern=self._convert_to_unix_path(child_of_root.attrib["name"]),
                                         subscribers=self._convert_str_to_list(child_of_root.attrib["author"]))
            _business_items.append(business_item)
        return _business_items

    def analyze_filemon(self):
        """解析filemon.xml文件
        :return: list - BusinessItem列表
        """
        _business_items = []
        tree = ET.ElementTree(file=self._file_mon)
        root = tree.getroot()
        if root.tag != "filemon":
            raise ConfigParseException(u"%s was invalid, because it didn't include <filemon> tag" % self._file_mon)
        for child_of_root in root:
            business_module = {}
            if child_of_root.tag != "business":
                raise ConfigParseException(u"%s was invalid，because it included invalid tag: "
                                           u"<%s>" % (self._file_mon, child_of_root.tag))
            business_module["name"] = child_of_root.attrib["name"]
            business_module["files"] = []
            for elem in child_of_root.iter():
                if elem.tag == "subject":  # 标题
                    business_module["subject"] = elem.text
                if elem.tag == "to":  # 关注人
                    business_module["subscribers"] = self._convert_str_to_list(elem.text)
                if elem.tag == "file":  # 文件
                    business_module["files"].append(self._convert_to_unix_path(elem.attrib["path"]))
            # convert dict to nametuple
            for f in business_module["files"]:
                business_item = BusinessItem(name=business_module["subject"],
                                             path_pattern=f,
                                             subscribers=business_module["subscribers"])
                _business_items.append(business_item)
        return _business_items

    def analyze_server(self):
        """解析服务端提供的业务模块信息
        :return: list - BusinessItem列表
        """
        _business_items = []
        for business_info in self._business_infos:
            _business_items.append(BusinessItem(name=business_info["name"],
                                                subscribers=business_info["subscribers"],
                                                path_pattern=business_info["path_pattern"]))
        return _business_items

    def analyze_business_relation(self):
        """解析服务端提供的业务集信息
        :return: list，BusinessRelation列表
        """
        _business_relations = []
        for _business_relation in self._business_relations:
            _business_relations.append(BusinessItem(name=_business_relation["name"],
                                                    path_pattern=_business_relation["path"],
                                                    subscribers=_business_relation["subscribers"]))
        return _business_relations


class Analysis(object):
    """cloc工具结果合并计算类
    """
    def __init__(self, file_data, task_params, business_items=None):
        """初始化函数
        :param file_data: dict - 文件代码数据
        :param include_patterns: list - 白名单列表
        :param exclude_patterns: list - 黑名单列表
        :param business_items: list - 业务模块列表
        """
        self._file_data = copy.copy(file_data)
        self._business_items = list(business_items) or []
        self._exclude_files = []
        self._include_files = []
        self._filter_util = FilterPathUtil(task_params, is_metric=True)

    @staticmethod
    def _match_path_pattern(path, pattern):
        """匹配path和pattern
        :param path: str - 文件路径
        :param pattern: str - 匹配字符串
        :return: Boolean - True 匹配成功，False匹配失败
        """
        # fnmatch.fnmatchcase 的实现原理：
        # 使用re编译pattern，然后将编译结果缓存起来（{pattern:re.compile(pattern)}, 最多缓存100个）
        # 接着再匹配path与pattern
        # 如果传入pattern时，先检查是否已经缓存的
        # 如果有就直接取缓存，如果没有缓存，则需要重新编译
        # 基于这种情况下，应该尽可能先利用已经缓存的编译，如果每次都重新编译，会非常耗时（相差100倍左右）
        if path.startswith(pattern) or fnmatch.fnmatchcase(path, pattern):
            return True
        return False

    def get_dir_info(self):
        """合并文件获取目录级别的代码统计信息
        :return: dict - 目录级别的代码统计信息
        """
        def _add_dir_info(dir_info, file_info):
            """将每个文件代码统计信息合并到目录统计信息中，并以树级结构记录
            :param dir_info: dict - 目录统计信息
            :param file_info: dict - 单个文件的代码统计信息
            """
            dir_path = file_info.get('dir_path', None)
            while dir_path is not None:
                dir_item = dir_info.setdefault(dir_path, {
                    "file_num": 0, "code_line_num": 0, "comment_line_num": 0,
                    "blank_line_num": 0, "total_line_num": 0, "mod_code_line_num": 0, "add_code_line_num": 0,
                    "del_code_line_num": 0, "mod_blank_line_num": 0, "add_blank_line_num": 0, "del_blank_line_num": 0,
                    "mod_comment_line_num": 0, "add_comment_line_num": 0, "del_comment_line_num": 0})
                dir_item["file_num"] += 1
                dir_item["code_line_num"] += file_info["code_line_num"]
                dir_item["comment_line_num"] += file_info["comment_line_num"]
                dir_item["blank_line_num"] += file_info["blank_line_num"]
                dir_item["total_line_num"] += file_info["total_line_num"]
                dir_item["mod_code_line_num"] += file_info["mod_code_line_num"]
                dir_item["add_code_line_num"] += file_info["add_code_line_num"]
                dir_item["del_code_line_num"] += file_info["del_code_line_num"]
                dir_item["mod_blank_line_num"] += file_info["mod_blank_line_num"]
                dir_item["add_blank_line_num"] += file_info["add_blank_line_num"]
                dir_item["del_blank_line_num"] += file_info["del_blank_line_num"]
                dir_item["mod_comment_line_num"] += file_info["mod_comment_line_num"]
                dir_item["add_comment_line_num"] += file_info["add_comment_line_num"]
                dir_item["del_comment_line_num"] += file_info["del_comment_line_num"]
                # logger.info("current dir_path: %s, data: %s" % (dir_path, dir_item))
                if dir_path:
                    dir_path = os.path.dirname(dir_path)
                else:
                    dir_path = None

        dir_result = {}
        for file_path, file_info in self._file_data.items():
            # 优先exclude文件再include指定文件
            if self._filter_util.should_filter_path(file_path):
                logger.info("add dir info, exclude file path: %s" % file_path)
                continue
            logger.info("add dir info, include file path: %s" % file_path)
            _add_dir_info(dir_result, file_info)
        return dir_result

    def _add_business_info(self, business_info, business_name, file_info):
        """将每个文件代码统计信息合并到业务模块统计信息中
        :param business_info: dict - 业务统计信息
        :param business_name: str - 业务模块名称
        :param file_info: dict - 单个文件的代码统计信息
        """
        business_module = business_info.setdefault(business_name, {
            "file_num": 0, "code_line_num": 0, "comment_line_num": 0,
            "blank_line_num": 0, "total_line_num": 0, "mod_code_line_num": 0, "add_code_line_num": 0,
            "del_code_line_num": 0, "mod_blank_line_num": 0, "add_blank_line_num": 0, "del_blank_line_num": 0,
            "mod_comment_line_num": 0, "add_comment_line_num": 0, "del_comment_line_num": 0})
        business_module["file_num"] += 1
        business_module["code_line_num"] += file_info["code_line_num"]
        business_module["comment_line_num"] += file_info["comment_line_num"]
        business_module["blank_line_num"] += file_info["blank_line_num"]
        business_module["total_line_num"] += file_info["total_line_num"]
        business_module["mod_code_line_num"] += file_info["mod_code_line_num"]
        business_module["add_code_line_num"] += file_info["add_code_line_num"]
        business_module["del_code_line_num"] += file_info["del_code_line_num"]
        business_module["mod_blank_line_num"] += file_info["mod_blank_line_num"]
        business_module["add_blank_line_num"] += file_info["add_blank_line_num"]
        business_module["del_blank_line_num"] += file_info["del_blank_line_num"]
        business_module["mod_comment_line_num"] += file_info["mod_comment_line_num"]
        business_module["add_comment_line_num"] += file_info["add_comment_line_num"]
        business_module["del_comment_line_num"] += file_info["del_comment_line_num"]

    def get_business_modules(self):
        """合并文件获取业务模块级别的代码统计
        :return: dict - 业务模块级别的代码统计信息
        """
        # 单进程操作时间：22 s，BusinessItem: 287, files: 37632, revisions: 324977 - 326653
        business_modules = {}
        if not len(self._business_items):
            return business_modules
        logger.debug("Business item count: %s" % len(self._business_items))

        for business_item in self._business_items:
            if not business_item.name:  # None or ""
                continue
            for file_path, file_info in self._file_data.items():
                if not self._match_path_pattern(file_path, business_item.path_pattern):
                    continue
                if business_item.name in file_info["business_names"]:
                    continue
                file_info["business_names"].append(business_item.name)
                file_info["subscribers"].extend(business_item.subscribers)
                file_info["subscribers"] = list(set(file_info["subscribers"]))
                self._add_business_info(business_modules, business_item.name, file_info)
        for file_path, file_info in self._file_data.items():
            if len(file_info["business_names"]) != 0:
                continue
            self._add_business_info(business_modules, "", file_info)  # business_name = ""
        return business_modules

    @staticmethod
    def _match_path(file_path, path_pattern, matched_path):
        """查看file_path是否以path_pattern开头且 path_pattern 比 matched_path 长
        :param file_path: str - 文件路径
        :param path_pattern: str - 匹配字符串
        :param matched_path: str - 已匹配的字符串
        :return: Boolean - True 匹配成功，False匹配失败
        """
        if file_path.startswith(path_pattern) and len(matched_path) < len(path_pattern):
            return True
        else:
            return False

    def get_business_relation_summary(self):
        """合并文件获取业务集的代码统计
        :return: dict - 业务集的代码统计信息
        """
        business_relation_summary = {}
        if not len(self._business_items):
            return business_relation_summary
        logger.debug("Business relation count: %s" % len(self._business_items))

        # 文件映射业务模块
        file_mappings = {}
        # 所有业务路径，一个路径可能属于多个业务，一个文件只属于一个路径

        business_path_list = set([business_relation.path_pattern for business_relation in self._business_items])
        # 将每个文件进行匹配
        for path in business_path_list:
            for file_path in self._file_data.keys():
                matched_path = file_mappings.setdefault(file_path, "")
                if self._match_path(file_path, path, matched_path):
                    logger.debug("file path matched success: %s(%s) -> %s" % (file_path, matched_path, path))
                    file_mappings[file_path] = path
        # 遍历，将文件与业务集的路径匹配并计算业务集数据
        for business_relation in self._business_items:
            for file_path, business_path in file_mappings.items():
                if business_relation.path_pattern == business_path:
                    logger.debug("business_relation matched path: %s -> %s" %
                                 (business_relation.path_pattern, business_path))
                    self._add_business_info(business_relation_summary,
                                            business_relation.name,
                                            self._file_data[file_path])
                    self._file_data[file_path]["business_names"].append(business_relation.name)
                    subscribers = business_relation.subscribers.split(";") if business_relation.subscribers else []
                    self._file_data[file_path]["subscribers"].extend(subscribers)
                    self._file_data[file_path]["subscribers"] = list(set(self._file_data[file_path]["subscribers"]))

        return business_relation_summary

    def get_language_summary(self):
        """获取语言类型概览数据
        """
        def _add_lang_info(lang_info, file_info):
            """将每个文件代码统计信息合并到语言统计信息中
            :param lang_info: dict - 语言统计信息
            :param file_info: dict - 单个文件的代码统计信息
            """
            language = file_info.get('language')
            if not language:
                return
            lang_item = lang_info.setdefault(language, {
                "file_num": 0, "code_line_num": 0, "comment_line_num": 0,
                "blank_line_num": 0, "total_line_num": 0, "mod_code_line_num": 0, "add_code_line_num": 0,
                "del_code_line_num": 0, "mod_blank_line_num": 0, "add_blank_line_num": 0, "del_blank_line_num": 0,
                "mod_comment_line_num": 0, "add_comment_line_num": 0, "del_comment_line_num": 0})
            lang_item["file_num"] += 1
            lang_item["code_line_num"] += file_info["code_line_num"]
            lang_item["comment_line_num"] += file_info["comment_line_num"]
            lang_item["blank_line_num"] += file_info["blank_line_num"]
            lang_item["total_line_num"] += file_info["total_line_num"]
            lang_item["mod_code_line_num"] += file_info["mod_code_line_num"]
            lang_item["add_code_line_num"] += file_info["add_code_line_num"]
            lang_item["del_code_line_num"] += file_info["del_code_line_num"]
            lang_item["mod_blank_line_num"] += file_info["mod_blank_line_num"]
            lang_item["add_blank_line_num"] += file_info["add_blank_line_num"]
            lang_item["del_blank_line_num"] += file_info["del_blank_line_num"]
            lang_item["mod_comment_line_num"] += file_info["mod_comment_line_num"]
            lang_item["add_comment_line_num"] += file_info["add_comment_line_num"]
            lang_item["del_comment_line_num"] += file_info["del_comment_line_num"]

        lang_result = {}
        for file_path, file_info in self._file_data.items():
            # 优先exclude文件再include指定文件
            if self._filter_util.should_filter_path(file_path):
                continue
            _add_lang_info(lang_result, file_info)
        return lang_result


class CodeCount(CodeMetricModel):
    """代码度量-CodeCount
    """

    version = "2.0"

    def __init__(self, params):
        """初始化函数
        """
        CodeMetricModel.__init__(self, params)

    def compile(self, params):
        pass

    def create_diff_files(self, scm_client, params, file_change_type, curr_dir, last_dir):
        """增量统计
        """
        logger.info("Increase scan task starts running...")
        # 注：获取差异异常原因：1. 版本号被回滚；
        try:
            diffs = SCMMgr(params).get_scm_diff()
            submodule_infos = SCMMgr(params).scm.get_submodule_infos()
        except Exception as err:
            logger.error("Get diff info failed, err: %s" % err)
            diffs = []
            submodule_infos = []

        if submodule_infos:
            submodule_paths = [item.path for item in submodule_infos]
        else:
            submodule_paths = []
        logger.info("current submodule path list: %s" % submodule_paths)
        filter_path_util = FilterPathUtil(params)
        # 3.1 获取差异代码文件
        for diff_info in diffs:
            # diff_info.path是git工具返回的，编码为utf8
            diff_info_path = diff_info.path
            if filter_path_util.should_filter_path(diff_info_path):
                logger.info("diff path: %s, should filter..." % diff_info_path)
                continue
            if not os.path.exists(os.path.join(params.source_dir, diff_info_path)) and diff_info.state != "del":
                logger.warning("diff_info path no exist: %s, skip...." % diff_info_path)
                continue
            logger.debug("diff path: %s, change_type: %s" % (diff_info_path, diff_info.state))
            # 忽略外链目录（会被识别为文件，实际应该是目录）
            if diff_info_path in submodule_paths:
                logger.info("find submodule dir: %s, ignoring" % diff_info_path)
                continue
            if os.path.exists(os.path.join(params.source_dir, diff_info_path)) and \
                    os.path.isdir(os.path.join(params.source_dir, diff_info_path)):
                logger.info("find dir: %s, ignoring" % diff_info_path)
                continue
            if os.path.islink(os.path.join(params.source_dir, diff_info_path)):
                logger.info("find link: %s, ignoring" % diff_info_path)
                continue
            file_change_type.update({diff_info_path.replace('\\', '/'): diff_info.state})
            if diff_info.state == "mod" or diff_info.state == "del":
                file_path = os.path.join(last_dir, diff_info_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                try:
                    # 注：git lfs本地不存在历史版本文件，直接获取会报异常，暂时忽略lfs文件统计
                    scm_client.get_file(diff_info_path, params["scm_last_revision"], file_path)
                except Exception as err:
                    logger.error("get file exception, file: %s, revision: %s, err: %s" % (
                        diff_info_path, params["scm_last_revision"], err))
            if diff_info.state == "mod" or diff_info.state == "add":
                file_path = os.path.join(curr_dir, diff_info_path)
                if not os.path.exists(os.path.dirname(file_path)):
                    os.makedirs(os.path.dirname(file_path))
                try:
                    # 先拷贝，如果捕获IOError异常，调用get_file方法获取
                    shutil.copyfile(os.path.join(params.source_dir, diff_info_path), file_path)
                except IOError:
                    logger.warning("diff_info path copy failed: %s, skip...." % diff_info_path)
                    scm_client.get_file(diff_info_path, params["scm_revision"], file_path)

    def analyze(self, params):
        """执行codecount 统计任务
        :param params: <dict> 任务执行请求
        :return: <list> 任务结果
        """
        # 1. 基本信息读取
        # 需要server 提供：scm路径、scm版本号区间、黑白名单路径配置、业务模块配置信息
        work_dir = os.getcwd()
        last_dir = os.path.join(work_dir, "last_files")
        curr_dir = os.path.join(work_dir, "curr_files")
        incr_scan = params.get("incr_scan", False)
        file_mon = params.get("filemon_path")
        file_mon = os.path.join(params.source_dir, file_mon) if file_mon else None
        core_file = params.get("corefile_path")
        core_file = os.path.join(params.source_dir, core_file) if core_file else None
        business_infos = params.get("business_infos")
        business_relations = params.get("business_relations", [])
        use_lang = params.get("use_lang", False)
        scan_languages = params.get("scan_languages", []) if use_lang else []
        code_count = ClocCountHandler(task_directory=work_dir, incr_scan=incr_scan,
                                      task_params=params,
                                      include_languages=scan_languages,
                                      is_metric=True)
        init_time = time.time()
        logger.debug("Core file path: %s" % core_file)
        logger.debug("File mon path: %s" % file_mon)
        logger.debug("Business infos: %s" % business_infos)
        logger.debug("Business relations: %s" % business_relations)
        logger.debug("Total code count dir: %s" % params.source_dir)
        # 2. 全量代码统计
        # update_task_progress(request, "代码统计工具开始扫描", 25)
        total = code_count.total_count(params.source_dir)
        total = code_count.filter_file_data(total)
        total_count_time = time.time()
        logger.info("Total code count finish: %s" % (total_count_time - init_time))
        # 3. 差异代码统计
        if incr_scan:
            file_change_type = {}
            get_file_time = time.time()
            scm_client = SCMMgr(params).get_scm_client()
            self.create_diff_files(scm_client, params, file_change_type, curr_dir, last_dir)
            get_file_time_end = time.time()
            logger.info("Get file time by scm client: %s" % (get_file_time_end - get_file_time))
            # 3.2 差异代码统计
            diff = code_count.diff_count(curr_dir, last_dir)
            diff = code_count.filter_file_data(diff)
            for file_path in diff.keys():
                if not diff[file_path].get("change_type"):  # change_type 不存在的情况下
                    diff[file_path]["change_type"] = file_change_type[file_path]
                if total.get(file_path):
                    total[file_path].update(diff[file_path])
                else:
                    total[file_path] = diff[file_path]
            logger.debug("Get diff count: %s" % (time.time() - get_file_time_end))
        incr_scan_time = time.time()
        logger.info("Increase scan task finishs: %s" % (incr_scan_time - total_count_time))
        logger.info("Business module & directory code count task starts running...")
        # 4.1 业务模块&目录的代码统计
        # update_task_progress(request, "过滤文件路径", 65)
        bc = BusinessConfig(core_file=core_file, file_mon=file_mon,
                            business_infos=business_infos, business_relations=business_relations)
        analysis = Analysis(file_data=total, task_params=params, business_items=bc.business_items)
        # 如果业务集存在，则只计算业务集
        if business_relations:
            logger.info("use business relation to count")
            business_data = analysis.get_business_relation_summary()
        else:
            logger.info("use business module to count")
            business_data = analysis.get_business_modules()
        logger.debug("Business module code count task finishs")

        get_business_time = time.time()
        logger.info("Get business time: %s" % (get_business_time - incr_scan_time))
        dir_data = analysis.get_dir_info()
        logger.info("Get directory time: %s" % (time.time() - get_business_time))
        logger.debug("Directory code count task finishs")
        lang_data = analysis.get_language_summary()
        result = self.format_result(total, dir_data, business_data, lang_data)
        # result = {"files": total, "dirs": dir_data, "business_module": business_data}
        # 5. 返回结果
        # update_task_progress(request, "代码统计工具完成扫描", 75)
        return result

    @staticmethod
    def format_result(file_data, dir_data, business_data, lang_data):
        """将文件、目录、业务模块代码统计数据转换为namedtuple类型

        :param file_data: dict - 文件级别代码统计信息
        :param dir_data: dict - 目录级别代码统计信息
        :param business_data: dict - 业务模块级别代码统计信息
        :param lang_data: dict - 语言级别代码统计信息
        :return: dict - 转换后的结果
                        {
                            "files": {
                                        "business_names": list, "subscribers": list,
                                        "cloc_tuple": namedtuple, "language": str, "change_type": str
                                     },
                            "dirs":  {"file_num": int, "cloc_tuple": namedtuple},
                            "business_modules": {"file_num": int, "cloc_tuple": namedtuple}
                            "cloc_tuple_definition": str
                        }
        """
        def _get_cloc_tuple(data):
            cloc_tuple = ClocTuple(code_line_num=data["code_line_num"],
                                   comment_line_num=data["comment_line_num"],
                                   blank_line_num=data["blank_line_num"],
                                   total_line_num=data["total_line_num"],
                                   add_code_line_num=data["add_code_line_num"],
                                   add_comment_line_num=data["add_comment_line_num"],
                                   add_blank_line_num=data["add_blank_line_num"],
                                   add_total_line_num=int(
                                       data["add_code_line_num"] + data["add_comment_line_num"] + data[
                                           "add_blank_line_num"]),
                                   mod_code_line_num=data["mod_code_line_num"],
                                   mod_comment_line_num=data["mod_comment_line_num"],
                                   mod_blank_line_num=data["mod_blank_line_num"],
                                   mod_total_line_num=int(
                                       data["mod_code_line_num"] + data["mod_comment_line_num"] + data[
                                           "mod_blank_line_num"]),
                                   del_code_line_num=data["del_code_line_num"],
                                   del_comment_line_num=data["del_comment_line_num"],
                                   del_blank_line_num=data["del_blank_line_num"],
                                   del_total_line_num=int(
                                       data["del_code_line_num"] + data["del_comment_line_num"] + data[
                                           "del_blank_line_num"])
                                   )
            return cloc_tuple

        _file_data = {}
        _dir_data = {}
        _business_data = {}
        _lang_data = {}
        if file_data:
            for file_path, file_info in file_data.items():
                _file_data[file_path] = {
                    # "dir_path": file_info["dir_path"], # Server端不需要该字段
                    "business_names": file_info["business_names"],
                    "subscribers": file_info["subscribers"],
                    "cloc_tuple": _get_cloc_tuple(file_info),
                    "language": file_info["language"],
                    "change_type": file_info["change_type"]
                }
        if dir_data:
            for dir_path, dir_info in dir_data.items():
                _dir_data[dir_path] = {
                    "file_num": dir_info["file_num"],
                    "cloc_tuple": _get_cloc_tuple(dir_info)
                }
        if business_data:
            for business_name, business_info in business_data.items():
                _business_data[business_name] = {
                    "file_num": business_info["file_num"],
                    "cloc_tuple": _get_cloc_tuple(business_info)
                }

        if lang_data:
            for language, lang_info in lang_data.items():
                _lang_data[language] = {
                    "file_num": lang_info["file_num"],
                    "cloc_tuple": _get_cloc_tuple(lang_info)
                }

        return {"files": _file_data, "dirs": _dir_data, "business_modules": _business_data, "langs": _lang_data,
                "cloc_tuple_definition": ' '.join(list(ClocTuple._fields))}

    def set_format_type(self):
        """
        通过覆盖该函数来选择format类型
        目前存在format类型有：
        1. NORMAL_FORMAT 常规format
        2. DUPLICATE_FORMAT 重复代码扫描的结果格式化
        由于format类型互斥，所以既能返回一个值
        :return:
        """
        return NO_FORMAT

    def set_filter_type_list(self):
        """
        通过覆盖该函数来选择过滤类型
        目前存在的过滤类型有：
        1. NO_FILTER  不需要过滤
        2. DIFF_FILTER 将非修改的代码文件进行过滤
        3. REVISION_FILTER 通过起始版本号进行过滤
        4. PATH_FILTER 通过用户设置的黑白名单进行过滤
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        """
        return [NO_FILTER]

    def set_submodule_handle(self):
        return NO_SUBMODULE_HANDLE

    def set_issue_hash(self):
        return NO_ISSUE_HASH

    def set_blame_type(self):
        """
        通过覆盖该函数来选择blame类型
        目前存在blame类型有：
        1. NO_BLAME 不需要blame
        2. NORMAL_BLAME 常规blame
        3. FILE_LAST_CHANGE_BLAME 将文件最后一个修改人作为责任人
        4. DUPLICATE_BLAME 获取重复代码块的最近修改信息
        由于blame类型互斥，所以既能返回一个值
        :return:
        """
        return NO_BLAME

    def set_result_pack_diff_info(self):
        # 代码统计不需要加入diff信息
        return False

    def set_add_file_info(self):
        # 不添加文件层级信息
        return NO_ADD_FILE_INFO


tool = CodeCount


if __name__ == "__main__":
    pass
