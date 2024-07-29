# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
本地任务执行器,只执行本地配置好的项目的扫描
"""
import json
import logging
import os
import sys
import time

from node.app import settings
from node.localtask.localconfig import LocalConfig
from node.localtask.localreport import LocalReport
from node.localtask.scminfo import ScmInfo, ScmAuthInfo
from node.localtask.localsrccheck import LocalSourcedir
from node.localtask.urlmgr import UrlMgr, UrlMap
from node.common.taskrunner import TaskRunner
from node.common.userinput import UserInput
from node.localtask.requestgenerator import TaskRequestGenerator
from util import errcode
from util.configlib import ConfigReader
from util.api.dogserver import RetryDogServer
from util.exceptions import NodeError, ResfulApiError
from util.pathlib import PathMgr
from util.scmurlmgr import BaseScmUrlMgr
from util.taskscene import TaskScene
from util.textutil import StringMgr
from util.logutil import LogPrinter
from util.cmdscm import ScmCommandError
from node.localtask.runlocaltask import RunTaskMgr
from node.localtask.projectmgr import ProjectMgr

logger = logging.getLogger(__name__)


class LocalRunner(TaskRunner):
    """本地任务执行器
    """
    # 启动场景类别
    CI_START = "CI"  # CI启动场景

    def __init__(self, args):
        """
        构造函数
        :param 命令行参数
        :return:
        """
        TaskRunner.__init__(self)
        self._origin_os_env = None

        # 任务心跳线程
        self._job_heartbeat = None

        self._args = args

        self._start_type = None  # 启动方式,是否为CI/CR启动
        self._token = None
        self._org_sid = None  # 团队编号
        self._team_name = None  # 项目名称
        self._source_dir = None
        self._languages = []
        self._scan_plan = None  # 分析方案名称
        self._branch = None
        self._scan_path = None
        self._total_scan = False  # 默认为False,即增量扫描
        self._exclude_paths = []
        self._include_paths = []
        self._pre_cmd = ""
        self._build_cmd = ""
        self._ref_scheme_id = None  # 参照扫描方案ID
        self._report_file = os.path.abspath("scan_status.json")  # 默认值

        self._labels = None
        self._proj_env = ""  # 项目环境变量,是一个字符串
        self._config_file = None
        self._admins = []

        self._compare_branch = None  # 对比分支
        self._scheme_templates = []  # 官方分析方案模板
        self._scheme_template_ids = []  # 官方分析方案模板id
        self._server_url = None  # 连接的 server url
        self._front_end_url = None  # 前端展示url,和server url是对应的
        self._scan_history_url = None  # 项目执行历史页面地址
        self._job_web_url = None
        self._create_from = "codedog_client"
        self._job_start_time = None  # 当前扫描任务开始时间,报给server,方便server计算和展示整个任务的执行时间
        self._repo_id = None  # 仓库id
        self._machine_tag = settings.OS_TAG_MAP[sys.platform]  # 执行机标签,默认根据当前机器操作系统决定,也允许用户指定
        # 启用的扫描组件,可选值:lint,cc,dup,cloc(代码检查、圈复杂度、重复代码、代码统计件),多项可用英文逗号(,)分隔,新建项目默认只启用代码检查组件
        self._enable_module = None
        # CI流水线任务的链接和触发人
        self._ci_job_url = None
        self._ci_job_trigger = None
        # 任务job id
        self._job_id = None
        # 任务名称和id的映射关系
        self._task_name_id_maps = {}

        self._scm_client = None
        self._scm_info = ScmInfo()
        self._scm_auth_info = ScmAuthInfo()
        self._proj_id = None

        self._skip_processes = {}

        # 与server通信的api实例
        self._dog_server = None

    def _get_value_from_config_file(self, config_dict, key, default=None):
        value = config_dict.get(key)
        if value:  # 判空
            return value
        else:
            return default

    def _read_config_file(self):
        """读取配置文件参数"""
        # 验证文件是否存在
        self._config_file = os.path.abspath(self._config_file)
        if not os.path.exists(self._config_file):
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG,
                            msg="配置文件(%s)不存在!" % self._config_file)

        # 读取配置文件内容
        config_dict = ConfigReader(cfg_file=self._config_file).read("config")
        self._token = self._get_value_from_config_file(config_dict, "token")
        self._org_sid = self._get_value_from_config_file(config_dict, "org_sid")
        self._team_name = self._get_value_from_config_file(config_dict, "team_name")
        self._source_dir = self._get_value_from_config_file(config_dict, "source_dir")
        languages_value = self._get_value_from_config_file(config_dict, "languages")
        if languages_value:
            self._languages = UserInput().format_languages(languages_value)
        self._scan_plan = self._get_value_from_config_file(config_dict, "scan_plan")
        self._branch = self._get_value_from_config_file(config_dict, "branch")
        self._scan_path = self._get_value_from_config_file(config_dict, "scan_path")
        total_scan_value = self._get_value_from_config_file(config_dict, "total_scan")
        if total_scan_value:
            self._total_scan = True if total_scan_value in ["True", "true"] else False
        self._compare_branch = self._get_value_from_config_file(config_dict, "compare_branch")
        exclude_value = self._get_value_from_config_file(config_dict, "exclude")
        if exclude_value:
            self._exclude_paths = StringMgr.str_to_list(exclude_value)
        include_value = self._get_value_from_config_file(config_dict, "include")
        if include_value:
            self._include_paths = StringMgr.str_to_list(include_value)
        self._pre_cmd = self._get_value_from_config_file(config_dict, "pre_cmd")
        self._build_cmd = self._get_value_from_config_file(config_dict, "build_cmd")
        self._ref_scheme_id = self._get_value_from_config_file(config_dict, "ref_scheme_id")
        self._scm_auth_info.ssh_file = self._get_value_from_config_file(config_dict, "ssh_file")
        report_file_value = self._get_value_from_config_file(config_dict, "report_file")
        if report_file_value:  # 判断非空时，才更新为指定值
            self._report_file = os.path.abspath(report_file_value)

    def _read_args(self, args):
        """
        读取命令行参数,命令行优先级更高,可覆盖配置文件参数
        """
        if args.token:
            self._token = args.token
        if args.org_sid:
            self._org_sid = args.org_sid
        if args.team_name:
            self._team_name = args.team_name
        if args.source_dir:
            self._source_dir = args.source_dir
        if args.language:
            self._languages = UserInput().format_languages(args.language)
        if args.pre_cmd:
            self._pre_cmd = args.pre_cmd
        if args.build_cmd:
            self._build_cmd = args.build_cmd
        if args.username:
            self._scm_auth_info.username = args.username
        if args.password:
            self._scm_auth_info.scm_password = args.password
        if args.branch:
            self._branch = args.branch
        if args.scan_path:
            self._scan_path = args.scan_path
        if args.compare_branch:
            self._compare_branch = args.compare_branch
        if args.exclude_paths:
            self._exclude_paths = StringMgr.str_to_list(args.exclude_paths)
        if args.include_paths:
            self._include_paths = StringMgr.str_to_list(args.include_paths)
        if args.ssh_file:
            self._scm_auth_info.ssh_file = args.ssh_file
        if args.total_scan:  # 命令行指定了全量扫描
            self._total_scan = args.total_scan
        if args.report_file:
            self._report_file = args.report_file
        if args.scan_plan:
            self._scan_plan = args.scan_plan
        if args.ref_scheme_id:
            self._ref_scheme_id = args.ref_scheme_id
        if args.server_url:
            self._server_url = args.server_url

    def _check_config_file(self, args):
        """判断使用哪个ini配置文件"""
        if args.config_file:
            self._config_file = os.path.abspath(args.config_file)
        else:
            self._config_file = os.path.join(settings.BASE_DIR, settings.CONFIG_NAME)
        if not os.path.exists(self._config_file):
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG,
                            msg='配置文件(%s)不存在,请确认是否已删除该文件.' % self._config_file)
        LogPrinter.info("using config file: %s" % self._config_file)

    def _read_and_check_args(self, args):
        """
        从命令行或配置文件读取本地扫描参数
        """
        self._start_type = args.start_type

        self._check_config_file(args)

        if self._config_file:
            self._read_config_file()

        self._read_args(args)

        # 如果没有命令行传参,先从config文件中获取,其次从环境变量获取,最后使用默认的server url
        if not self._server_url:
            self._server_url = LocalConfig.get_server_url(self._config_file)

        if not self._server_url:
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="Server url为空, 请在ini配置文件中输入服务端地址!")

        # 根据server url,获取对应的前端展示url
        self._front_end_url = UrlMap.get_frontend_url(self._server_url)

        # 打印连接的sever前端地址
        LogPrinter.info("connect to server: %s" % self._front_end_url)

        # 先确认是否有token
        if not self._token:
            token_url = UrlMgr(self._front_end_url, org_sid=self._org_sid,
                               team_name=self._team_name).get_user_info_url()
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG,
                            msg="未输入认证令牌(Token)信息,没有CodeDog扫描权限,请先补充Token参数再启动.\n"
                                "Token获取方式:浏览器打开%s,复制Token." % token_url)

        self._check_scan_path()

    def _check_scan_path(self):
        """检查scan_path，并添加到过滤路径中"""
        if self._scan_path:  # 先判空，避免未传值时是None
            # 删除前后空格
            self._scan_path = self._scan_path.strip()
            # 如果包含头尾斜杠，去掉
            self._scan_path = self._scan_path.strip('/')
        if self._scan_path:
            if self._source_dir:
                # 检查指定的目录是否存在
                scan_full_path = os.path.join(self._source_dir, self._scan_path)
                if not os.path.exists(scan_full_path):
                    raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=f"scan path {self._scan_path} not exists!")
            # 添加到include路径中
            self._include_paths.append(f"{self._scan_path}/*")

    def __check_config_info(self):
        """
        验证用户输入的配置信息是否符合要求
        :return: 不符合要求,直接抛异常
        """
        if not self._source_dir:
            if self._start_type == self.CI_START:
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="缺少-s参数,未输入本地代码目录!")
            logger.warning("未输入本地代码目录,请补充信息!")
            self._source_dir = UserInput().input_source_dir()
            if not self._source_dir:
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="本地代码目录输入有误!")

        # 有source_dir时,校验 source_dir
        if self._source_dir:
            # 验证本地代码目录是否存在
            self._source_dir = PathMgr().format_path(self._source_dir)
            # 兼容软链接的情况,如果是软链接,转换成所指向的真实代码目录
            self._source_dir = os.path.realpath(self._source_dir)
            if not os.path.exists(self._source_dir):
                if self._start_type == self.CI_START:
                    raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="代码目录(%s)不存在" % self._source_dir)
                logger.warning("代码目录(%s)不存在" % self._source_dir)
                # 提示用户重新输入
                self._source_dir = UserInput().input_source_dir()
                if not self._source_dir:
                    raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="输入异常,退出!")
            # 自动获取scm_type
            git_config_dir = os.path.join(self._source_dir, ".git")
            svn_config_dir = os.path.join(self._source_dir, ".svn")
            if os.path.exists(git_config_dir) and os.path.exists(svn_config_dir):
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG,
                                msg="代码目录(%s)下同时存在.svn和.git目录,无法判断scm类型!" % self._source_dir)
            if os.path.exists(git_config_dir):
                self._scm_info.scm_type = "git"
            elif os.path.exists(svn_config_dir):
                self._scm_info.scm_type = "svn"
            else:
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG,
                                msg="代码目录(%s)下不包含.svn或.git目录,不是有效代码库!" % self._source_dir)

            # 验证本地代码目录是否符合要求
            self._scm_client, self._scm_info = LocalSourcedir(self._scm_info,
                                                              self._source_dir,
                                                              self._branch).check_local_source_dir()

            # 如果本地代码目录是ssh鉴权方式,没有指定ssh file参数时,使用系统默认的ssh file
            if not self._scm_auth_info.ssh_file:
                ssh_scm_type = BaseScmUrlMgr.check_ssh_scm_type(self._scm_info.scm_url)  # 如果是ssh方式,返回git或svn,否则返回None
                # git不需要代码权限，svn blame时才需要访问远端server
                if ssh_scm_type and ssh_scm_type == 'svn':
                    from util.scmcache import SshFlieClient
                    self._scm_auth_info.ssh_file = SshFlieClient.get_default_ssh_file()

        # 有ssh私钥文件路径时,校验文件是否存在
        if self._scm_auth_info.ssh_file:
            self._scm_auth_info.ssh_file = PathMgr().format_path(self._scm_auth_info.ssh_file)
            if not os.path.exists(self._scm_auth_info.ssh_file):
                raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg="SSH秘钥文件(%s)不存在!" % self._scm_auth_info.ssh_file)

        # 校验self._report_file
        if self._report_file:
            self._report_file = PathMgr().format_path(self._report_file)

    def _get_proj_config(self, repo_id, proj_id, org_sid, team_name):
        """
        根据项目id获取项目参数
        :param proj_id: 项目id
        :return:
        """
        try:
            return self._dog_server.get_proj_conf(org_sid, team_name, repo_id, proj_id)
        except ResfulApiError as error:
            err_msg = "获取CodeDog项目配置信息失败.可能是个人token无该项目权限,或项目配置有误.请申请权限,或检查项目配置信息!\n%s" % error.msg
            raise NodeError(code=errcode.E_NODE_TASK_CONFIG, msg=err_msg)

    def run(self):
        """执行本地项目扫描
        """
        LogPrinter.info(f"start from {self._create_from}.")
        self._job_start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))

        try:
            # 获取参数，并判断参数合法性
            self._read_and_check_args(self._args)

            # 如果历史结果文件json存在,先清理掉,以免影响本次扫描
            report_filepath = os.path.abspath(self._report_file)
            if os.path.exists(report_filepath):
                PathMgr().rmpath(report_filepath)

            # 创建一个与serve通信的API类实例
            self._dog_server = RetryDogServer(self._server_url, self._token).get_api_server(retry_times=2)

            os.environ["TaskScene"] = TaskScene.LOCAL

            # 保存当前环境变量,执行子进程时使用该环境变量,避免被污染
            self._origin_os_env = dict(os.environ)

            # 校验输入的配置信息是否正确,如果有问题,提示重新输入
            self.__check_config_info()

            # 没有指定项目ID,根据本地代码url判断是否已有项目,没有则新建项目
            project_mgr = ProjectMgr(self._scan_plan, self._scheme_template_ids,
                                     self._scheme_templates, self._languages,
                                     self._dog_server, self._org_sid, self._team_name, self._source_dir,
                                     self._include_paths, self._exclude_paths,
                                     self._proj_id, self._scm_info, self._report_file, self._admins,
                                     self._scm_auth_info, self._front_end_url,
                                     self._labels, self._machine_tag, self._ref_scheme_id, self._proj_env,
                                     self._create_from, self._enable_module)
            self._repo_id, self._proj_id = project_mgr.check_and_create_proj(self._scan_path)

            # 获取任务执行参数
            proj_conf = self._get_proj_config(self._repo_id, self._proj_id, self._org_sid, self._team_name)
            # with open("proj_conf.json", "w") as wf:
            #     json.dump(proj_conf, wf, indent=2)

            # 获取实际使用的扫描方案名称
            self._scan_plan = proj_conf["job_context"]["scheme_name"]
            self._repo_id = proj_conf["job_context"]["repo_id"]

            url_mgr_client = UrlMgr(self._front_end_url, self._repo_id, self._proj_id, org_sid=self._org_sid,
                                    team_name=self._team_name)
            proj_overview_url = url_mgr_client.get_proj_overview_url()
            LogPrinter.info("Project url: %s" % proj_overview_url)
            self._scan_history_url = url_mgr_client.get_scan_history_url()

            # 解析项目配置,获取当前可以直接执行的task request list
            request_generator = TaskRequestGenerator(
                self._dog_server, self._source_dir, self._total_scan,
                self._scm_info, self._scm_auth_info, self._scm_client,
                self._report_file, self._server_url, self._scan_history_url,
                self._job_web_url, self._exclude_paths, self._include_paths,
                self._pre_cmd, self._build_cmd,
                self._origin_os_env, self._repo_id, self._proj_id,
                self._org_sid, self._team_name, self._create_from,
                self._compare_branch
            )

            cur_execute_request_list, self._skip_processes, self._job_id, self._job_heartbeat, self._task_name_id_maps, remote_task_names = \
                request_generator.generate_request(proj_conf)

            # 此时已经有job_id，生成job页面
            self._job_web_url = url_mgr_client.get_job_url(self._job_id)

            # 根据参数对项目进行扫描
            run_task_mgr = RunTaskMgr(self._source_dir, self._total_scan, self._proj_id, self._job_id, self._repo_id,
                                      self._token, self._dog_server, self._server_url, self._job_web_url,
                                      self._scm_client, self._scm_info, self._scm_auth_info, self._task_name_id_maps,
                                      remote_task_names, self._origin_os_env, self._job_start_time,
                                      self._create_from, self._scan_history_url, self._report_file,
                                      self._org_sid, self._team_name, self._skip_processes)
            run_task_mgr.scan_project(cur_execute_request_list, proj_conf)
        except Exception as err:
            # 优先使用：job页面 > 扫描历史页面 > 主页
            if self._job_web_url:
                url = self._job_web_url
            elif self._scan_history_url:
                url = self._scan_history_url
            else:
                url = self._front_end_url

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
                "url": url,
                "text": "扫描异常",
                "description": description,
                "scan_report": {}
            }
            LocalReport.output_report(scan_result, self._report_file)
            LogPrinter.exception(description)
        finally:
            # 停止任务心跳线程
            if self._job_heartbeat:
                self._job_heartbeat.stop()


if __name__ == '__main__':
    pass
