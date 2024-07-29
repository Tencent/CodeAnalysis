# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
节点模式,通过轮询不断从server获取任务并执行
"""

import json
import os
import time

from node.app import settings
from node.localtask.localconfig import LocalConfig
from node.servertask.nodemgr import NodeMgr, HeartBeat, NodeStatusMonitor
from node.common.task import Task
from node.common.taskdirmgr import TaskDirCtl
from node.common.taskrunner import TaskRunner
from node.common.uploadresult import ResultUploader
from util.crypto import Crypto
from util.api.dogserver import RetryDogServer
from util.reporter import Reporter, InfoType
from util.taskscene import TaskScene
from task.toolmodel import IToolModel
from util.errcode import E_NODE_TASK
from util.exceptions import FileServerError
from util.logutil import LogPrinter
from util.cleaner import Cleaner


class LoopRunner(TaskRunner):
    """轮询任务执行器,通过轮询不断获取任务来执行
    """
    def __init__(self, args):
        """构造函数
        """
        TaskRunner.__init__(self)

        self._token = args.token
        self._tag = args.tag
        self._org_sid = args.org_sid
        self._create_from = args.create_from if args.create_from else "codedog_client"
        self._server_url = LocalConfig.get_server_url()
        # 打印启动渠道和连接的sever地址
        LogPrinter.info(f"start from {self._create_from}.")
        LogPrinter.info("using server: %s" % self._server_url)
        # 初始化与codedog服务器通信的api server实例
        self._server = RetryDogServer(self._server_url, self._token).get_api_server()
        self._get_task_interval = 10  # sec,获取任务频率

        # 设置环境变量，标记是节点模式
        os.environ["TaskScene"] = TaskScene.NORMAL
        # 初始环境变量,保存下来,执行子进程时使用该环境变量,避免被污染
        self._origin_os_env = dict(os.environ)

    def _handle_exist_task(self):
        """管理当前在执行的任务,如果任务结束,上传分析结果,并从self._running_task列表中删除
        """
        for task in self._running_task[:]:
            if task.done:
                LogPrinter.info('task %s with id %d is done', task.task_name, task.task_id)
                # 从任务队列中删除
                self._running_task.remove(task)
                # 上传结果到server
                self._send_result(task)
                # # 分析任务完成后,按照磁盘空间和创建时间清理数据
                # LogPrinter.info("clean data directory ...")
                # SourceManager.del_old_file()

    def _terminate_task(self, task_id):
        """kill task"""
        for task in self._running_task[:]:
            if task and task.task_id == task_id:
                task.terminate()
                self._running_task.remove(task)
                LogPrinter.info('terminate task %d by server', task_id)

    def _send_result(self, task):
        """
        上传结果
        :param task: 任务实例
        :return:
        """
        """send task result to server"""
        if task.code is None: # 分析正常完成的情况
            with open(task.response_file, 'r') as fp:
                task_response = json.load(fp)
            code = task_response['status']
            data = task_response['result']
            msg = task_response['message']
            node_task_version = task_response['task_version']

        else: # 分析异常退出情况
            code = task.code
            data = task.data
            msg = task.msg
            node_task_version = IToolModel.version

        LogPrinter.info('uploading task(%s) result(code:%d) to server', task.task_name, code)

        # 上传分析结果
        with open(task.request_file) as rf:
            task_request = json.load(rf)
            job_id = task_request['job']
            task_dir = task_request["task_dir"]
            execute_processes = task_request['execute_processes']
            project_id = task_request['task_params'].get('project_id')

        # 上报进度: 98% - 上传分析结果
        Reporter(task_request['task_params']).update_task_progress(InfoType.SendResult)

        try:
            # 上传issues和log到文件服务器
            data_url, log_url = ResultUploader().upload_result_detail(project_id, task.task_id, task_dir, data, task.task_log)
        except FileServerError as err:
            code = err.code
            msg = f"Fail to send result to file server! Error: {err.msg}"
            data_url = ""
            log_url = ""
            LogPrinter.error(msg)
        except Exception as err:  # 捕获其他异常,避免影响后续上报结果给server（导致server任务卡住无法结束）
            code = E_NODE_TASK
            msg = f"Fail to send result to file server! Error: {str(err)}"
            data_url = ""
            log_url = ""
            LogPrinter.error(msg)

        # 上报结果给server
        self._server.send_task_result(task_request['task_params'], job_id, task.task_id, node_task_version, code, data_url, msg, log_url, execute_processes)

        # 2019-11-18 注释掉,这里加了没用,上传完结果server端task已经不在运行
        # util.exceptions.ResfulApiError: Error[218]: Error[400]: {"task":["指定Task已经不在运行中"]}
        # # 上报进度: 100% - 任务完成
        # Reporter(task_params).update_task_progress(InfoType.TaskDone)
        LogPrinter.info('result upload finished')
        # 2021-09-09 注释掉 因为上报完后task已结束，会报异常：Error[400]: {'task': ['指定Task已经不在运行中']}
        # # 上报进度: 100% - 子任务执行结束
        # Reporter(task_request['task_params']).update_task_progress(InfoType.TaskDone)

    def _modify_include_paths(self, task_request):
        """（适配大仓场景）将scan_path添加到过滤路径include中,指定扫描对应的目录"""
        task_params = task_request['task_params']
        scan_path = task_params.get("scan_path")
        if scan_path:  # 判空，避免值为None的情况
            # 删除前后空格
            scan_path = scan_path.strip()
            # 如果包含头尾斜杠，去掉（包含默认扫描整个仓库时的传值/）
            scan_path = scan_path.strip('/')
        if scan_path:
            format_scan_path = f"{scan_path}/*"
            include_paths = task_params["path_filters"]["inclusion"]
            if format_scan_path not in include_paths:  # 如果有上一阶段，已经添加到include路径，不需要重复添加
                include_paths.append(format_scan_path)

    def run(self):
        """looprunner主函数"""
        # 向server注册节点
        NodeMgr().register_node(self._server, self._tag, self._org_sid, self._create_from)

        # 启动心跳上报线程
        HeartBeat(self._server).start()

        # 启动机器状态上报线程
        NodeStatusMonitor(self._server).start()

        # 启动轮询获取任务,执行分析
        LogPrinter.info("task loop is started.")

        while True:
            try:
                # 管理在执行的任务
                self._handle_exist_task()
            except:
                LogPrinter.exception("_handle_exist_task error, skip and continue ...")

            try:
                # 获取任务
                if self._running_task:  # 有任务在跑，不空闲
                    node_is_free = False
                else:  # 任务队列为空，空闲
                    node_is_free = True
                task_request = self._server.get_task(node_is_free)
                if not task_request:
                    # 获取不到任务,休息一段时间再继续获取
                    time.sleep(self._get_task_interval)
                    continue

                if ('task_params' not in task_request) or (task_request['task_params'] is None):
                    LogPrinter.exception("task_params not exists or is null!\ntask_request: %s" % json.dumps(task_request, indent=2))
                    LogPrinter.info("reset task_params to empty dict.")
                    task_request['task_params'] = {}
                task_params = task_request.get('task_params', {})
                task_name = task_request.get('task_name')
                job_id = task_request.get('job')
                task_version = task_request.get("task_version")

                # kill task任务中，task_request没有id字段,需要从task_params中获取
                if task_name == '_kill_task':
                    task_id = task_params.get("task_id")
                else:
                    task_id = task_request.get('id')

                LogPrinter.info("node is free: %s, get task: name=%s, id=%d, task_version=%s" % (node_is_free, task_name, task_id, task_version))

                # 获取到kill_task任务
                # kill_task任务参数 {'task_name': '_kill_task', 'task_id':0, 'task_params':{'task_id': xxx}}
                if task_name == '_kill_task':
                    kill_task_id = task_params['task_id']
                    # kill task时进程如果已不存在,会报异常: ProcessLookupError: [Errno 3] No such process
                    self._terminate_task(kill_task_id)
                    # 等待一段时间后再接下一个任务
                    time.sleep(self._get_task_interval)
                    continue

                # 获取到分析任务，向server发送确认信息(kill_task不需要确认)
                if task_id is not None:
                    self._server.confirm_task(task_id)

                # 获取到分析任务时,先根据磁盘空间和创建时间情况清理数据
                try:
                    LogPrinter.info("clean data directory ...")
                    Cleaner.del_old_file()
                except Exception as err:
                    LogPrinter.exception("encounter error when clean data dir: %s", str(err))

                # 获取任务执行目录
                task_dir, task_id = TaskDirCtl().acquire_task_dir(task_id)

                task_request['task_dir'] = task_dir

                # 在param中添加task_scene信息,标记任务运行场景
                task_request['task_params']['task_scene'] = TaskScene.NORMAL
                # 将job_id, task_id, token, server_url放到task_params中,供task进度上报和代码行上报使用
                task_request['task_params']['task_id'] = task_id
                task_request['task_params']['job_id'] = job_id
                task_request['task_params']['token'] = Crypto(settings.PASSWORD_KEY).encrypt(self._token)  # token加密
                task_request['task_params']['server_url'] = self._server_url

                # 大仓场景，指定目录扫描，需要将扫描目录添加到include过滤路径中
                self._modify_include_paths(task_request)

                task_log = os.path.join(task_dir, 'task.log')
                request_file = os.path.join(task_dir, 'task_request.json')
                response_file = os.path.join(task_dir, 'task_response.json')

                with open(request_file, 'w') as wf:
                    json.dump(task_request, wf, indent=2)

                task = Task(task_id, task_name, request_file, response_file, task_log, env=self._origin_os_env)
                task.start()
                self._running_task.append(task)
                # 等待一段时间后再接下一个任务
                time.sleep(self._get_task_interval)
            except:
                # 遇到异常,输出异常信息
                LogPrinter.exception("task loop encounter error.")
                # 如果希望节点遇到异常不退出，避免掉线，可以注释掉raise
                raise
