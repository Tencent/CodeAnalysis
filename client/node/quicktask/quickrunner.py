# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
QuickRunner
"""

import json
import logging
import os
import sys

from node.localtask.runtask import ConcurrentTasksRuner
from node.localtask.localconfig import LocalConfig
from node.common.taskdirmgr import TaskDirCtl
from node.common.taskrunner import TaskRunner
from node.common.userinput import UserInput
from node.quicktask.quickscan import QuickScan
from util import errcode
from util.api.dogserver import RetryDogServer
from util.exceptions import NodeError
from util.pathlib import PathMgr
from util.scmurlmgr import BaseScmUrlMgr
from util.taskscene import TaskScene
from util.checklanguage import LanguageChecker
from util.logutil import LogPrinter
from util.cmdscm import ScmCommandError
from util.textutil import StringMgr

logger = logging.getLogger(__name__)


class QuickRunner(TaskRunner):
    def __init__(self, args):
        """
        构造函数
        :param 命令行参数
        :return:
        """
        TaskRunner.__init__(self)
        self._origin_os_env = None

        self._args = args
        # 命令行参数
        if args.source_dir:
            self._source_dir = args.source_dir
        else:
            self._source_dir = None
        if args.file:
            self._scan_files = StringMgr.str_to_list(args.file)
            if not self._source_dir:
                LogPrinter.error(f"source dir is empty, please use --source-dir argument.")
                sys.exit(-1)
            for rel_path in self._scan_files:
                if not os.path.exists(os.path.join(self._source_dir, rel_path)):
                    LogPrinter.error(f"{rel_path} path not exists!")
                    sys.exit(-1)
        else:
            self._scan_files = []
        if args.language:
            self._languages = UserInput().format_languages(args.language)
        else:
            self._languages = []
        if args.label:
            self._labels = StringMgr.str_to_list(args.label)
        else:
            self._labels = []
        if args.token:
            self._token = args.token
        else:
            self._token = None
        if args.scheme_template_id:
            self._scheme_template_id = args.scheme_template_id
        else:
            self._scheme_template_id = None
        if args.org_sid:
            self._org_sid = args.org_sid
        else:
            self._org_sid = None

        # 其他变量
        self._scm_type = None
        self._languages = []
        self._ssh_file = None

        self._report_file = os.path.abspath("scan_status.json")  # 默认值
        self._scan_history_url = None  # 项目执行历史页面地址

        # 其他成员变量,通过计算得到
        self._scm_client = None
        self._scm_revision = None
        self._scm_url = None
        self._total_scan = True

        # 本地执行的任务目录路径
        self._local_task_dirs = []
        # 需要扫描的文件相对路径
        self._scan_rel_paths = []
        # 扫描的文件信息，包含path,lines
        self._path_info = {}

    def _output_result(self, result):
        """
        输出分析结果
        :param result:
        :return:
        """
        # 输出到json文件
        with open(self._report_file, "wb") as status_obj:
            status_obj.write(str.encode(json.dumps(result, indent=2, ensure_ascii=False)))

        task_rules, task_result_paths = self.get_task_result_paths(result, self._local_task_dirs)
        QuickScan().generate_qucik_scan_report(self._path_info, result, task_result_paths, task_rules)

    def get_task_result_paths(self, result, local_task_dirs):
        task_rules = {}
        task_result_paths = {}
        from node.localtask.status import StatusType
        if result.get("status") == StatusType.SUCCESS:
            for task_dir in local_task_dirs:
                task_request_file = os.path.join(task_dir, "task_request.json")
                with open(task_request_file, 'r') as rf:
                    task_request = json.load(rf)
                    execute_processes = task_request["execute_processes"]
                    task_name = task_request.get("task_name")
                    if QuickScan.is_quick_scan():
                        if task_name not in ["cpd", "lizard", "codecount"]:
                            task_rules[task_name] = task_request["task_params"]["rule_list"]
                            task_result_paths[task_name] = os.path.join(task_dir, "task_response.json")
                    else:
                        if "datahandle" in execute_processes:
                            if task_name in ["cpd", "codecount"]:
                                task_result_paths[task_name] = os.path.join(task_dir, "task_response.json")
                            else:
                                task_result_paths[task_name] = os.path.join(task_dir, "workdir/issue_dir")
        return task_rules, task_result_paths

    def _get_scm_url(self, scm_info):
        """
        从本地代码scm info中获取scm url
        :param scm_info:
        :return:
        """
        if not scm_info.url:
            err_msg = "本地代码库获取不到 [origin标签] 远程代码库链接，" \
                      "请在代码目录下检查确认是否为空: git config --get remote.origin.url," \
                      "并执行以下命令进行设置：git remote add origin ${代码库链接}"
            raise NodeError(code=errcode.E_NODE_TASK_SCM_FAILED, msg=err_msg)
        format_url = BaseScmUrlMgr.format_url(scm_info.url)
        if self._scm_type == "git":
            if "master" == scm_info.branch:  # 为了兼容旧版,master分支直接只用url,不加分支名
                return format_url
            else:
                return "%s#%s" % (format_url, scm_info.branch)
        else:
            raise NodeError(code=errcode.E_NODE_TASK_SCM_FAILED, msg="不支持的scm类型: %s!" % self._scm_type)

    def _check_config_info(self):
        """
        验证用户输入的配置信息是否符合要求
        :return: 不符合要求,直接抛异常
        """
        if not self._source_dir:
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="缺少-s参数,未输入本地代码目录!")

        # 有source_dir时,校验 source_dir
        if self._source_dir:
            # 验证本地代码目录是否存在
            self._source_dir = PathMgr().format_path(self._source_dir)
            # 兼容软链接的情况,如果是软链接,转换成所指向的真实代码目录
            self._source_dir = os.path.realpath(self._source_dir)
            if not os.path.exists(self._source_dir):
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="代码目录(%s)不存在" % self._source_dir)

    def _check_no_language_exit(self):
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
            self._output_result(scan_result)
            sys.exit(0)  # 正常退出

    def check_language(self, input_params):
        """
        如果未指定语言，根据需要扫描的文件自动识别语言
        :return:
        """
        # 快速分析模式，如果没有语言参数，自动识别语言
        if not self._languages:
            language_types = set()
            logger.info(f"{len(self._scan_rel_paths)} files to scan: {self._scan_rel_paths}")
            for file_path in self._scan_rel_paths:
                file_language = LanguageChecker.get_file_language_type(file_path)
                if file_language:
                    language_types.add(file_language)
            self._languages = list(language_types)
            LogPrinter.info(f"languages: {self._languages}")

    def _merge_path_filters(self, default_filtered_paths, path_filters):
        return {
            "inclusion": path_filters["inclusion"] + default_filtered_paths["inclusion"],
            "exclusion": path_filters["exclusion"] + default_filtered_paths["exclusion"],
            "re_inclusion": path_filters["re_inclusion"] + default_filtered_paths["re_inclusion"],
            "re_exclusion": path_filters["re_exclusion"] + default_filtered_paths["re_exclusion"]
        }

    def _generate_request(self, proj_conf, path_filters):
        """
        根据项目配置信息生成任务参数列表
        :param proj_conf: 项目配置信息
        :return: 当前可直接执行的任务参数列表
        """
        job_context = proj_conf["job_context"]
        # 全量分析
        job_context["incr_scan"] = False
        # 合并过滤路径
        new_path_filters = self._merge_path_filters(job_context["path_filters"], path_filters)

        task_list = proj_conf["tasks"]

        for task_request in task_list:
            task_params = task_request.get("task_params")
            task_params["incr_scan"] = False
            task_params["scm_last_revision"] = ""
            task_params["path_filters"] = new_path_filters
            task_params["scm_url"] = self._scm_url
            task_params["scm_type"] = self._scm_type
            task_params["project_id"] = job_context.get("project_id")

            task_request["execute_processes"] = task_request["processes"]
            task_request["private_processes"] = []

            # 添加task_scene信息,标记任务运行场景
            task_request['task_params']['task_scene'] = TaskScene.LOCAL
            # 添加 source_dir 和 scm_type
            if self._source_dir:
                task_request['task_params']['source_dir'] = self._source_dir
            # 添加 task_dir 信息
            task_dir, task_id = TaskDirCtl().acquire_task_dir()
            task_request['id'] = task_id
            task_request['task_dir'] = task_dir
            task_request['task_params']['task_id'] = task_id

        return task_list

    def _scan_project(self, execute_request_list):
        """
        根据参数对项目进行分析
        :param execute_request_list: list, 当前可以在本地直接执行的任务参数列表
        :return:
        """
        # QuickScan默认使用并发扫描
        proj_scan_succ, finished_task_results, error_code, error_msg = ConcurrentTasksRuner(execute_request_list,
                                                                                            self._origin_os_env,
                                                                                            None,
                                                                                            None).run()
        for task_result in finished_task_results:
            task_dir = os.path.dirname(task_result.request_file)
            self._local_task_dirs.append(task_dir)

        scan_result = QuickScan.get_result(proj_scan_succ, error_code, error_msg)
        self._output_result(scan_result)

    def run(self):
        """执行本地项目分析
        """
        try:
            os.environ["TaskScene"] = TaskScene.LOCAL
            os.environ["TCA_QUICK_SCAN"] = "True"  # 标记为快速扫描模式，方便后续判断

            # 保存当前环境变量,执行子进程时使用该环境变量,避免被污染
            self._origin_os_env = dict(os.environ)

            # 校验输入的配置信息是否正确,如果有问题,提示重新输入
            self._check_config_info()

            # 获取任务执行参数
            input_params = QuickScan.get_input_params(self._scan_files)
            # LogPrinter.info(f">>> input_params: {json.dumps(input_params, indent=2)}")
            self._scan_rel_paths, self._path_info = QuickScan.get_scan_paths(input_params, self._source_dir)
            self.check_language(input_params)
            # LogPrinter.info(f">>> input_params: {json.dumps(input_params, indent=2)}")
            if self._scheme_template_id:
                if self._token and self._org_sid:  # 通过server获取指定的分析方案模板的任务参数
                    LogPrinter.info(f"token and scheme_template_id are set, get task config from server ...")
                    server_url = LocalConfig.get_server_url()
                    dog_server = RetryDogServer(server_url, self._token).get_api_server(retry_times=2)
                    proj_conf = dog_server.get_jobconfs_by_scheme_template(self._scheme_template_id, self._org_sid)
                else:
                    raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="已输入scheme_template_id, "
                                                                         "但缺少--token和--org-sid参数, "
                                                                         "无法获取到分析方案模板, 请补充参数!")
            else:
                proj_conf = QuickScan.get_proj_config(self._scm_url, self._languages, self._labels, input_params)

            # debug打印调试
            # with open("quickscan_proj_config.json", "w") as wf:
            #     json.dump(proj_conf, wf, indent=2)

            # 将需要扫描的文件添加到项目过滤路径中
            path_filters = QuickScan.get_path_filters(input_params)

            # 根据参数对项目进行分析
            execute_request_list = self._generate_request(proj_conf, path_filters)
            self._scan_project(execute_request_list)
            return "OK"
        except Exception as err:
            # 异常封装处理：
            # ScmCommandError 是cmdscm抛的异常，统一封装成 client 异常 E_NODE_TASK_SCM_FAILED 上报
            # 其他未知异常，统一报 E_NODE_TASK
            if isinstance(err, ScmCommandError):
                error_code = errcode.E_NODE_TASK_SCM_FAILED
            else:
                error_code = getattr(err, 'code', errcode.E_NODE_TASK)

            description = "%s: %s" % (type(err).__name__, err)
            scan_result = {
                "status": "error",
                "error_code": error_code,
                "text": "分析异常",
                "description": description,
                "scan_report": {}
            }
            self._output_result(scan_result)
            LogPrinter.exception("quickscan encounter error.")
            return "Error"
