# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
用于对扫描结果进行blame处理
"""


import threading
import logging
import os
import locale

from queue import Queue
from datetime import datetime
from multiprocessing import cpu_count
from util.exceptions import TaskBlameError
from util.reporter import Reporter, InfoType
from task.scmmgr import SCMMgr
from task.basic.datahandler.handlerbase import HandlerBase
from util.scanlang.callback_queue import CallbackQueue

logger = logging.getLogger(__name__)

# blame类型
NO_BLAME = 0
NORMAL_BLAME = 1
FILE_LAST_CHANGE_BLAME = 2
DUPLICATE_BLAME = 3
CCN_BLAME = 4

# blame异常检测阈值
BLAME_BASE = 3
BLAME_FAILURE_RATE = 0.6
BLAME_ERROR_NUM = 0

# blame阈值检测开关，通过环境变量控制
BLAME_RATE_ENV = "BLAME_RATE_MONITOR"


class Blamer(HandlerBase):
    def run(self, params):
        """
        执行blame操作
        :param params: 初始结果
        :return: blame后的结果
        """
        if self.handle_type == NO_BLAME:
            return params
        elif self.handle_type == NORMAL_BLAME:
            Reporter(params).update_task_progress(InfoType.BlameTask)
            return self._lint_blame(params)
        elif self.handle_type == FILE_LAST_CHANGE_BLAME:
            Reporter(params).update_task_progress(InfoType.BlameTask)
            return self._file_last_change_blame(params)
        elif self.handle_type == DUPLICATE_BLAME:
            Reporter(params).update_task_progress(InfoType.BlameTask)
            return self._duplicate_blame(params)
        elif self.handle_type == CCN_BLAME:
            Reporter(params).update_task_progress(InfoType.BlameTask)
            return self._ccn_blame(params)
        raise TaskBlameError("blame type is not exist: %s" % self.handle_type)

    def _lint_blame(self, params):
        """
        执行blame
        :param params:
        :return:
        """
        logger.info("Start: lint blame.")

        fileissues = params["result"]
        source_dir = params["source_dir"]

        # 获取sourcedir最近一次提交的版本号和时间，作为blame失败时的默认提交版本和时间
        scm_mgr = SCMMgr(params)
        scm_info = scm_mgr.get_scm_client().info()
        latest_commit_revision, latest_commit_time = scm_info.commit_revision, scm_info.commit_time

        logger.info("Start to blame ...")

        que = Queue()

        def blame_worker():
            # 每个线程需要独立创建一个scmclient实例，否则执行blame会出现错误
            while not que.empty():
                fileissue = que.get()
                issues = fileissue.get("issues", False)
                if not issues:
                    que.task_done()
                    continue
                path = fileissue.get("path")
                try:
                    logger.info("blame: %s" % os.path.join(source_dir, path))
                    blames = scm_mgr.blame(os.path.join(source_dir, path))
                except Exception as e:
                    logger.exception("blame exception: %s - %s", str(e), path)
                    blames = None
                # logger.info('insert issues: %s' % os.path.join(source_dir, path))
                for issue in issues:
                    if not blames:
                        # blame失败，author置为空，使用默认提交版本和时间
                        global BLAME_ERROR_NUM
                        BLAME_ERROR_NUM = BLAME_ERROR_NUM + 1
                        logger.error("%s blame fail! use empty author, default revision and ci_time." % path)
                        issue["author"] = ""
                        issue["author_email"] = None
                        issue["revision"] = latest_commit_revision
                        issue["ci_time"] = latest_commit_time
                    else:
                        # blame成功，使用blame获取的信息
                        try:
                            issue['line'] = int(issue['line'])
                            if "end_line" in issue:
                                blame_infos = blames[issue["line"] - 1 : issue["end_line"]]
                                blame_info = max(blame_infos, key=lambda x: x.timestamp)
                            else:
                                blame_info = blames[issue["line"] - 1]
                            issue["author"] = blame_info.author
                            issue["author_email"] = blame_info.email
                            issue["revision"] = blame_info.revision
                            issue["ci_time"] = blame_info.timestamp
                            # issue['column'] = 0 # 统一重置为0，暂缓之计
                        except Exception as ex:
                            logger.exception(
                                "path:%s, line_num:%s, len(blames):%s, blames:\n%s exception: %s",
                                path,
                                issue["line"],
                                len(blames),
                                blames,
                                ex,
                            )
                            # 异常情况处理，author置为空，使用默认提交版本和时间
                            issue["author"] = ""
                            issue["author_email"] = None
                            issue["revision"] = latest_commit_revision
                            issue["ci_time"] = latest_commit_time
                    # logger.info('insert issue done.')
                # logger.info('insert issues done.')
                que.task_done()

        for fileissue in fileissues:
            que.put(fileissue)

        # 由于cc不支持多线程，所以此处特殊处理，cc通过单线程调用
        if que.qsize() <= 8:
            thread_num = 1
        else:
            # 调整为根据cpu数量设置
            thread_num = cpu_count()

        # 多线程下使用datetime.datetime.strptime会出现线程安全问题
        # AttributeError: 'module' object has no attribute '_strptime'
        # 原因：strptime 函数第一次调用时是非线程安全的，因为第一次调用会 import _strptime.
        # import _strptime操作是非线程安全的，会抛出异常 AttributeError 或 ImportError
        # 为了规避这个问题，在使用线程之前要先调用一次 strptime 函数，后面再调用的时候就是线程安全的
        try:
            datetime.strptime("2018-03-27T19:42:45.290531Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        except Exception as err:
            logger.error("Parse blame timestamp error: %s. Set locale and retry..." % err)
            # 问题说明：在部分windows机器上会出现  ValueError: embedded null byte，属于 windows C运行库的Bug
            # 解决方案：设置 LC_ALL 为 en 可以解决该问题
            # python论坛说明：https://bugs.python.org/issue25023
            locale.setlocale(locale.LC_ALL, "en")
            datetime.strptime("2018-03-27T19:42:45.290531Z", "%Y-%m-%dT%H:%M:%S.%fZ")

        # 为了防止code平台异常导致blame失败，从而提交有问题的结果上报到server，需要做一个失败验证
        # 因此打算共设置两个值，基础值b和阈值比例Φ
        # 当（b+blame失败的数量）/（b+总量）> Φ 则判定为失败
        blame_num = que.qsize()
        logger.info("start blame thread.")
        for _ in range(thread_num):
            t = threading.Thread(target=blame_worker, name="blame_worker")
            t.daemon = True
            t.start()
        que.join()

        logger.info("结束blame，BLAME_ERROR_NUM: %d，blame_num：%d" % (BLAME_ERROR_NUM, blame_num))

        blame_rate_monitor = os.environ.get(BLAME_RATE_ENV, "true")

        # 如果扫描未提交代码，不检查blame失败阈值
        if os.getenv("TCA_UNCOMMITTED_CODE") == "True":
            logger.info(f"env TCA_UNCOMMITTED_CODE=True, skip checking BLAME_FAILURE_RATE({BLAME_FAILURE_RATE}).")
        else:
            if BLAME_ERROR_NUM > BLAME_BASE and blame_num > BLAME_BASE and blame_rate_monitor.lower() == "true":
                # 分子分母都减去基数是为了增加对小项目的容忍度
                if (BLAME_ERROR_NUM - BLAME_BASE) / (blame_num - BLAME_BASE) > BLAME_FAILURE_RATE:
                    raise TaskBlameError("blame 失败次数超过预设阈值，请检查是否由于code平台异常导致或调整阈值后重试。")

        params["result"] = fileissues

        logger.info("End: lint blame.")
        # logger.info(params['result'])

        return params

    def __blame_file_callback__(self, fileissue, scm_client, source_dir, latest_commit_revision, latest_commit_time):
        """
        多线程并发回调,获取文件最后修改人
        :param fileissue:
        :param scm_client:
        :param source_dir:
        :param latest_commit_revision:
        :param latest_commit_time:
        :return:
        """
        issues = fileissue.get("issues", False)
        if not issues:
            return
        path = fileissue.get("path")
        try:
            scm_log = scm_client.log(f'"{os.path.join(source_dir, path)}"', limit=1)
        except Exception as e:
            logger.exception("scm_log exception: %s - %s", str(e), path)
            scm_log = None
        if not scm_log:
            # 获取log失败，author置为空，使用默认提交版本和时间
            author = ""
            author_email = None
            revision = latest_commit_revision
            timestamp = latest_commit_time
        else:
            # 获取log成功，使用log获取的信息
            try:
                author = scm_log[0].author
                author_email = scm_log[0].email
                revision = scm_log[0].revision
                timestamp = scm_log[0].timestamp
            except IndexError as err:
                logger.error(
                    "cannot find file's last change info for %s, error: %s, scm_log: %s. use default value."
                    % (path, err, scm_log)
                )
                # 异常情况处理，author置为空，使用默认提交版本和时间
                author = ""
                author_email = None
                revision = latest_commit_revision
                timestamp = latest_commit_time

        for issue in issues:
            issue["author"] = author
            issue["author_email"] = author_email
            issue["revision"] = revision
            issue["ci_time"] = timestamp
            # issue['column'] = 0 # 统一重置为0，暂缓之计

    def _file_last_change_blame(self, params):
        """
        获取文件最后修改人为责任人，针对非代码文件实现
        :param params:
        :return:
        """
        logger.info("Start: blame file last change author.")
        fileissues = params["result"]
        source_dir = params["source_dir"]
        scm_client = SCMMgr(params).get_scm_client()

        # 获取sourcedir最近一次提交的版本号和时间，作为blame失败时的默认提交版本和时间
        scm_info = SCMMgr(params).get_scm_client().info()
        latest_commit_revision, latest_commit_time = scm_info.commit_revision, scm_info.commit_time

        callback_queue = CallbackQueue(min_threads=50, max_threads=1000)
        for fileissue in fileissues:
            callback_queue.append(
                self.__blame_file_callback__,
                fileissue,
                scm_client,
                source_dir,
                latest_commit_revision,
                latest_commit_time,
            )
        callback_queue.wait_for_all_callbacks_to_be_execute_and_destroy()

        logger.info("End: blame file last change author.")
        return params

    def _duplicate_blame(self, params):
        """
        获取重复代码块的最近修改信息
        :param params:
        :return:
        """
        logger.info("Start: blame duplicate code's author.")
        fileissues = params["result"]
        source_dir = params["source_dir"]
        scm_mgr = SCMMgr(params)

        # update blame info
        que = Queue()

        def blame_worker():
            while not que.empty():
                fileissue = que.get()
                path = fileissue.get("path", False)
                if not path:
                    que.task_done()
                    continue

                try:
                    logger.info("blame: %s" % os.path.join(source_dir, path))
                    blames = scm_mgr.blame(os.path.join(source_dir, path))
                except Exception as e:
                    logger.exception("blame exception: %s - %s", str(e), path)
                    blames = None
                if not blames:
                    logger.error("cannot get blame info for %s" % path)
                    fileissue["last_modifier"] = ""
                else:
                    fileissue["last_modifier"] = max(blames, key=lambda x: x.timestamp).author

                for issue in fileissue["code_blocks"]:
                    if not blames:
                        # blame失败，author置为空，使用默认提交版本和时间
                        logger.error("%s blame fail! use empty author, default revision and ci_time." % path)
                        issue["last_modifier"] = ""
                        issue["related_modifiers"] = ""
                    else:
                        try:
                            # line block blame
                            blame_infos = blames[issue["start_line_num"] - 1 : issue["end_line_num"]]
                            blame_info = max(blame_infos, key=lambda x: x.timestamp)

                            issue["last_modifier"] = blame_info.author
                            related_modifiers = list()
                            related_modifiers.append(issue["last_modifier"])
                            for blame_author in blame_infos:
                                bauthor = blame_author.author
                                if bauthor.rfind(")") != -1:
                                    bauthor = bauthor.split("(")[0]
                                if (bauthor not in related_modifiers) and len(related_modifiers) < 10:
                                    related_modifiers.append(bauthor)
                            issue["related_modifiers"] = ";".join(related_modifiers)

                        except Exception as e:
                            logger.exception("exception: %s", str(e))
                            logger.exception(
                                "path:%s, start_line_num:%s, len(blames):%s, blames:%s\n",
                                path,
                                issue["start_line_num"],
                                len(blames),
                                blames,
                            )
                            issue["last_modifier"] = ""
                            issue["related_modifiers"] = ""
                que.task_done()

        thread_num = cpu_count()
        for fileissue in fileissues:
            que.put(fileissue)
        for _ in range(thread_num):
            t = threading.Thread(target=blame_worker, name="blame_worker")
            t.daemon = True
            t.start()
        que.join()

        params["result"] = fileissues
        logger.info("End: duplicate blame.")
        return params

    def _ccn_blame(self, params):
        """
        获取圈复杂度的最近修改信息
        :param params:
        :return:
        """
        logger.info("Start: ccn blame.")

        fileissues = params["result"]["detail"]
        source_dir = params["source_dir"]
        scm_mgr = SCMMgr(params)

        # 获取sourcedir最近一次提交的版本号和时间，作为blame失败时的默认提交版本和时间
        scm_info = scm_mgr.get_scm_client().info()
        latest_commit_revision, latest_commit_time = scm_info.commit_revision, scm_info.commit_time

        # update blame info
        que = Queue()

        def blame_worker():
            while not que.empty():
                fileissue = que.get()
                issues = fileissue.get("issues", [])
                path = fileissue.get("path", False)
                if not path:
                    que.task_done()
                    continue
                try:
                    blames = scm_mgr.blame(os.path.join(source_dir, path))
                except Exception as e:
                    logger.exception("blame exception: %s - %s", str(e), path)
                    blames = None

                # 计算文件层级的负责人
                if blames:
                    blame_info = max(blames, key=lambda x: x.timestamp)
                    fileissue["last_modifier"] = str(blame_info.author).strip()
                    fileissue["last_modifier_email"] = blame_info.email
                    fileissue["revision"] = blame_info.revision
                    fileissue["ci_time"] = blame_info.timestamp
                    related_modifiers = list()
                    related_modifiers.append(fileissue["last_modifier"])
                    for blame_author in blames:
                        bauthor = str(blame_author.author).strip()
                        # logger.debug(bauthor)
                        if bauthor.rfind(")") != -1:
                            bauthor = bauthor.split("(")[0]
                        if bauthor not in related_modifiers:
                            related_modifiers.append(bauthor)
                        if len(related_modifiers) >= 10:
                            break
                    fileissue["related_modifiers"] = ";".join(related_modifiers)
                    weight_modifiers = self._get_weight_blames(blames)
                    modifier_keys = list(weight_modifiers.keys())
                    fileissue["weight_modifiers"] = ";".join(modifier_keys)
                    fileissue["most_weight_modifier"] = modifier_keys[0]
                    fileissue["most_weight_modifier_email"] = weight_modifiers[modifier_keys[0]]["email"]
                else:
                    fileissue["last_modifier"] = ""
                    fileissue["related_modifiers"] = ""
                    fileissue["weight_modifiers"] = ""
                    fileissue["most_weight_modifier"] = ""
                    fileissue["most_weight_modifier_email"] = ""
                    fileissue["revision"] = latest_commit_revision
                    fileissue["ci_time"] = latest_commit_time

                for issue in issues:
                    tmp = dict()
                    # blame失败时候的默认值
                    tmp["modifier"] = ""
                    tmp["related_modifiers"] = ""
                    tmp["weight_modifiers"] = ""
                    tmp["most_weight_modifier"] = ""
                    tmp["most_weight_modifier_email"] = ""
                    tmp["revision"] = latest_commit_revision
                    tmp["ci_time"] = latest_commit_time

                    if not blames:
                        # blame失败，author置为空，使用默认提交版本和时间
                        logger.error("%s blame fail! use empty author, default revision and ci_time." % path)
                    elif issue["start_line_no"] > len(blames):
                        logger.info(f"issue起始行号大于文件行数: path: {path} issue: {issue} blame: {blames}")
                    else:
                        try:
                            # 获取责任人
                            blame_infos = blames[issue["start_line_no"] - 1 : issue["end_line_no"]]
                            blame_info = max(blame_infos, key=lambda x: x.timestamp)
                            tmp["modifier"] = str(blame_info.author).strip()
                            tmp["revision"] = blame_info.revision
                            tmp["ci_time"] = blame_info.timestamp
                            related_modifiers = list()
                            related_modifiers.append(tmp["modifier"])
                            for blame_author in blame_infos:
                                bauthor = str(blame_author.author).strip()
                                # logger.debug(bauthor)
                                if bauthor.rfind(")") != -1:
                                    bauthor = bauthor.split("(")[0]
                                if (bauthor not in related_modifiers) and (len(related_modifiers) < 10):
                                    related_modifiers.append(bauthor)
                            tmp["related_modifiers"] = ";".join(related_modifiers)
                            weight_modifiers = self._get_weight_blames(blames)
                            modifier_keys = list(weight_modifiers.keys())
                            tmp["weight_modifiers"] = ";".join(modifier_keys)
                            tmp["most_weight_modifier"] = modifier_keys[0]
                            tmp["most_weight_modifier_email"] = weight_modifiers[modifier_keys[0]]["email"]
                        except (IndexError, ValueError) as e:
                            logger.exception(
                                "path:%s, start_line_no:%s, end_line_no:%s\n",
                                path,
                                issue["start_line_no"],
                                issue["end_line_no"],
                            )

                    issue["modifier"] = tmp["modifier"]
                    issue["related_modifiers"] = tmp["related_modifiers"]
                    issue["weight_modifiers"] = tmp["weight_modifiers"]
                    issue["most_weight_modifier"] = tmp["most_weight_modifier"]
                    issue["most_weight_modifier_email"] = tmp["most_weight_modifier_email"]
                    issue["revision"] = tmp["revision"]
                    issue["ci_time"] = tmp["ci_time"]
                que.task_done()

        thread_num = cpu_count()
        for fileissue in fileissues:
            que.put(fileissue)
        for _ in range(thread_num):
            t = threading.Thread(target=blame_worker, name="blame_worker")
            t.daemon = True
            t.start()
        que.join()

        logger.info("End: ccn blame.")

        return params

    def _get_weight_blames(self, blame_infos):
        """
        依据行数占比计算每个修改人的权重，返回权重人列表。降序
        {
            "name1": {
                "email": "name1@example.com",
                "counter": 10,
            },
            "name2": {
                "email": "name1@example.com",
                "counter": 5,
            },
        }
        """
        weight_modifiers = dict()
        for blame_author in blame_infos:
            bauthor = str(blame_author.author).strip()
            # logger.debug(bauthor)
            if bauthor.rfind(")") != -1:
                bauthor = bauthor.split("(")[0]
            if bauthor not in weight_modifiers:
                weight_modifiers[bauthor] = {
                    "email": blame_author.email,
                    "counter": 0,
                }
            weight_modifiers[bauthor]["counter"] += 1
        # 排序
        return dict(sorted(weight_modifiers.items(), key=lambda i: i[1]["counter"], reverse=True))

    @staticmethod
    def get_tool_handle_type_name():
        return "set_blame_type"
