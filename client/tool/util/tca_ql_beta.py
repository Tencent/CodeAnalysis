# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
 ______   ______     ______        ______     __        
/\__  _\ /\  ___\   /\  __ \      /\  __ \   /\ \       
\/_/\ \/ \ \ \____  \ \  __ \     \ \ \/\_\  \ \ \____  
   \ \_\  \ \_____\  \ \_\ \_\     \ \___\_\  \ \_____\ 
    \/_/   \/_____/   \/_/\/_/      \/___/_/   \/_____/ 
                                                        
"""


import os
import shutil
import json

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from util.api.fileserver import RetryFileServer
from util.configlib import ConfigReader
from util.envset import EnvSet
from util.errcode import E_NODE_TASK_PARAM
from util.exceptions import TaskError
from util.pathfilter import FilterPathUtil
from util.pathlib import PathMgr
from util.subprocc import SubProcController
from util.logutil import LogPrinter
from task.codelintmodel import CodeLintModel
from task.basic.common import subprocc_log
from task.scmmgr import SCMMgr


logger = LogPrinter()

lang_map = {
    "python": [".py"],
    "php": [".php"],
    "go": [".go"],
    "cpp": ["cpp", "c", "C", "cc", "cxx", "h", "hxx", "hpp"],
}


class TcaQlBeta(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)

    def __download_database(self, params, path):
        base_dir = f"tcaql/repos/{params.repo_id}"
        try:
            file_name = os.path.join(base_dir, f"{path}.db")
            db_path = os.path.join(params["work_dir"], "db", f"{path}.db")
            logger.info(f"开始下载文件{file_name}")
            file_server = RetryFileServer(retry_times=2).get_server()
            if file_server.download_file(file_name, db_path):
                logger.info("下载成功")
                return True
        except:
            logger.warning("下载失败")
            return False

    def __upload_database(self, params, path):
        logger.info("准备上传到云端存储数据库")
        base_dir = f"tcaql/repos/{params.repo_id}"
        try:
            logger.info("开始上传")
            upload_file_name = os.path.join(base_dir, f"{path}.db")
            db_dir = os.path.join(params["work_dir"], "db")
            file_name = os.path.join(db_dir, f"{path}.db")
            file_server = RetryFileServer(retry_times=2).get_server()
            file_server.upload_file(file_name, upload_file_name)
            logger.info("上传成功")
        except:
            logger.warning("上传失败")
            return False

    def __generate_config_file(self, rule_list, work_dir, source_dir, toscans):
        """生成分析用的配置文件"""
        setting_file = os.path.join(work_dir, "config.xml")
        if os.path.exists(setting_file):
            os.remove(setting_file)
        config_data = ET.Element("hades")
        source_data = ET.SubElement(config_data, "sourcedir")
        source_data.text = source_dir
        checker_data = ET.SubElement(config_data, "checkers")
        for rule in rule_list:
            checker = ET.SubElement(checker_data, "checker")
            checker_name = ET.SubElement(checker, "name")
            checker_name.text = rule["name"]
            rule_params = rule["params"]
            if rule_params:
                rule_params = rule_params.split("<br>")
                for rule_param in rule_params:
                    if "[hades]" not in rule_param:
                        rule_param = "[hades]\r\n" + rule_param
                    rule_param_dict = ConfigReader(cfg_string=rule_param).read("hades")
                    for key, value in rule_param_dict.items():
                        param = ET.SubElement(checker, "param")
                        param.text = value
                        param.set("param_name", key)
        files = ET.SubElement(config_data, "filelist")
        for scan in toscans:
            file = ET.SubElement(files, "file")
            file.text = scan
        tree = ET.ElementTree(config_data)
        tree.write(setting_file, encoding="utf-8")
        return setting_file

    def compile(self, params, lang):
        source_dir = params.source_dir
        logger.info("开始编译项目 %s" % source_dir)
        work_dir = params.work_dir
        db_dir = os.path.join(work_dir, "db")
        repo_id = params.repo_id
        envs = os.environ
        ZEUS_HOME = envs.get("ZEUS_BETA_HOME", None)
        scm_revision = params["scm_revision"]
        db_name = f"{repo_id}_{scm_revision}_{lang}"
        db_path = os.path.join(db_dir, db_name + ".db")
        inc = params["incr_scan"]
        logger.info("是否为增量编译: %s" % inc)
        if not os.path.exists(db_dir):
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
        if inc:
            last_scm_revision = params["scm_last_revision"]
            last_db_name = f"{repo_id}_{last_scm_revision}_{lang}"
            last_db_path = os.path.join(db_dir, last_db_name + ".db")
            logger.info(f"下载上个成功分析版本数据库{last_db_name}")
            if not self.__download_database(params, last_db_name):
                logger.info("下载数据库失败将重新生成")
            else:
                shutil.copyfile(last_db_path, db_path)
                want_suffix = lang_map[lang]
                diffs = SCMMgr(params).get_scm_diff()
                toscans = [diff.path.replace(os.sep, "/") for diff in diffs if diff.path.endswith(tuple(want_suffix))]
                inc_build_cmd = [
                    "./Zeus",
                    "inc_compile",
                    "-l",
                    lang,
                    "-p",
                    db_name,
                    "-db",
                    db_dir,
                    "-s",
                    source_dir,
                    "-f",
                ]
                logger.info(inc_build_cmd)
                pre_cmd_len = len(inc_build_cmd)
                CMD_ARG_MAX = PathMgr().get_cmd_arg_max()
                LogPrinter.info("命令行长度限制：%d" % CMD_ARG_MAX)
                cmd_args_list = PathMgr().get_cmd_args_list(inc_build_cmd, toscans, CMD_ARG_MAX)
                for cmd in cmd_args_list:
                    tmp_cmd = inc_build_cmd + [",".join(cmd[pre_cmd_len:])]
                    sp = SubProcController(
                        command=tmp_cmd,
                        cwd=ZEUS_HOME,
                        stdout_line_callback=subprocc_log,
                        stderr_line_callback=subprocc_log,
                    )
                    sp.wait()
                    logger.info(sp.returncode)
                self.__upload_database(params, db_name)
                return
        # 全量编译命令
        full_build_cmd = [
            "./Zeus",
            "compile",
            "-p",
            db_name,
            "-db",
            db_dir,
            "-l",
            lang,
            "-s",
            source_dir,
        ]
        logger.info(full_build_cmd)
        sp = SubProcController(
            command=full_build_cmd,
            cwd=ZEUS_HOME,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
        )
        sp.wait()
        logger.info(sp.returncode)
        self.__upload_database(params, db_name)
        return

    def analyze(self, params, lang):
        source_dir = params.source_dir
        relpos = len(source_dir) + 1
        work_dir = params.work_dir
        db_dir = os.path.join(work_dir, "db")
        repo_id = params.repo_id
        envs = os.environ
        HADES_HOME = envs.get("HADES_BETA_HOME", None)
        scm_revision = params["scm_revision"]
        db_name = f"{repo_id}_{scm_revision}_{lang}"
        db_path = os.path.join(db_dir, db_name + ".db")
        if not os.path.exists(db_path):
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            logger.info(f"本地未找到数据库文件{db_path}，从文件服务器下载")
            if not self.__download_database(params, db_name):
                raise TaskError(E_NODE_TASK_PARAM, "数据库读取失败可能为选错了语言")
        rules = params["rule_list"]
        inc = params["incr_scan"]
        want_suffix = lang_map[lang]
        if inc:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [
                diff.path.replace(os.sep, "/")
                for diff in diffs
                if diff.path.endswith(tuple(want_suffix)) and diff.state != "del"
            ]
        else:
            toscans = [
                path.replace(os.sep, "/")[relpos:] for path in PathMgr().get_dir_files(source_dir, tuple(want_suffix))
            ]
        # 过滤文件以及过滤文件取相对路径
        toscans = FilterPathUtil(params).get_include_files([os.path.join(source_dir, path) for path in toscans], relpos)
        toscans = [path[relpos:] for path in toscans]
        toscans = PathMgr().format_cmd_arg_list(toscans)
        if not toscans:
            logger.warning("分析文件为空")
            if os.path.exists(db_path):
                self.__upload_database(params, db_name)
            return []
        output_json = os.path.join(work_dir, "result.json")
        setting_file = self.__generate_config_file(rules, work_dir, source_dir, toscans)
        analyze_cmd = [
            "./Hades",
            "analyze",
            "-l",
            lang,
            "-db",
            db_path,
            "-o",
            output_json,
            "-c",
            setting_file,
        ]
        logger.info(analyze_cmd)
        task_dir = os.path.dirname(os.getcwd())
        request_file = os.path.abspath(os.path.join(task_dir, "task_request.json"))
        os.environ["TASK_REQUEST"] = request_file
        issues = []
        sp = SubProcController(
            command=analyze_cmd,
            cwd=HADES_HOME,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            env=EnvSet().get_origin_env(),
        )
        sp.wait()
        if os.path.exists(output_json):
            with open(output_json, "r") as result_reader:
                result = json.load(result_reader)
                issues.extend(result)
        else:
            logger.warning("未生成结果文件")
        if os.path.exists(db_path):
            self.__upload_database(params, db_name)
        return issues


tool = TcaQlBeta

if __name__ == "__main__":
    pass
