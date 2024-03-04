# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
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
from util.textutil import CodecClient
from util.pathfilter import FilterPathUtil
from util.pathlib import PathMgr
from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from task.basic.common import subprocc_log
from util.subprocc import SubProcController
from util.zipmgr import Zip
from util.logutil import LogPrinter
from task.authcheck.check_license import __lu__


logger = LogPrinter()

lang_map = {
    "python": [".py"],
    "php": [".php"],
    "go": [".go"],
    "cpp": [".cpp", ".c", ".C", ".cc", ".cxx", ".h", ".hxx", ".hpp"],
    "js": [".js", ".jsx"],
}


class TcaQl(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)

    # 没有使用mysql数据库，采用sqlite所以需要文件服务器存储数据用于增量分析
    # 如果使用mysql数据库可以考虑替换掉数据库地址参数代替下载上传数据文件
    def __download_database(self, params, path):
        """下载之前存储的数据库，增量使用"""
        base_dir = f"tcaql/repos/{params.repo_id}"
        try:
            file_name = os.path.join(base_dir, f"{path}.zip")
            db_path = os.path.join(params["work_dir"], "db")
            zip_file = os.path.join(db_path, f"{path}.zip")
            logger.info(f"开始下载文件{file_name}")
            file_server = RetryFileServer(retry_times=2).get_server()
            if file_server.download_big_file(file_name, zip_file):
                logger.info("下载成功")
                Zip().decompress_by_7z(zip_file, db_path)
                os.remove(zip_file)
                return True
            else:
                return False
        except Exception as e:
            logger.warning(f"下载失败")
            return False

    def __upload_database(self, params, path):
        """上传数据库"""
        logger.info("准备上传到云端存储数据库")
        base_dir = f"tcaql/repos/{params.repo_id}"
        try:
            logger.info("开始上传")
            upload_file_name = os.path.join(base_dir, f"{path}.zip")
            cache_dir = os.path.join(params["work_dir"], "db")
            cache_zip = os.path.join(params["work_dir"], f"{path}.zip")
            if os.path.exists(cache_zip):
                os.remove(cache_zip)
            if Zip().compress(cache_dir, cache_zip):
                file_server = RetryFileServer(retry_times=2).get_server()
                file_server.upload_file(cache_zip, upload_file_name)
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

    def __get_zeus_version(self, params):
        # 2023/1/10 调整获取Zeus版本的方式
        envs = os.environ
        ZEUS_HOME = envs.get("ZEUS_HOME", None)
        work_dir = params.work_dir
        scan_cmd = self.get_cmd(
            "Zeus",
            [
                "--version",
            ],
        )
        lang_ext_output = os.path.join(work_dir, "Zeus_version.txt")
        spc = SubProcController(
            scan_cmd,
            cwd=ZEUS_HOME,
            stdout_line_callback=subprocc_log,
            stderr_line_callback=subprocc_log,
            stdout_filepath=lang_ext_output,
        )
        spc.wait()

        fi = open(lang_ext_output, "rb")
        # 读取文件内容并解码为字符串
        content = CodecClient().decode(fi.read())
        fi.close()
        return content.split(" ")[-1].strip()

    def compile(self, params, lang):
        """
        编译函数，指代码生成数据流
        """
        source_dir = params.source_dir
        relpos = len(source_dir) + 1
        logger.info("开始编译项目 %s" % source_dir)
        work_dir = params.work_dir
        db_dir = os.path.join(work_dir, "db")
        repo_id = params.repo_id
        envs = os.environ
        ZEUS_HOME = envs.get("ZEUS_HOME", None)
        scm_revision = params["scm_revision"]
        version = self.__get_zeus_version(params)
        db_name = f"{repo_id}_{scm_revision}_{lang}_{version}"
        db_path = os.path.join(db_dir, f"{db_name}.db")
        inc = params["incr_scan"]
        want_suffix = lang_map[lang]
        logger.info("是否为增量编译: %s" % inc)
        file_list = os.path.join(work_dir, "filelist.txt")
        if not os.path.exists(db_dir):
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
        if self.__download_database(params, db_name):
            if os.path.exists(db_path):
                return
        if inc:
            last_scm_revision = params["scm_last_revision"]
            last_db_name = f"{repo_id}_{last_scm_revision}_{lang}_{version}"
            last_db_path = os.path.join(db_dir, last_db_name + ".db")
            logger.info(f"下载上个成功分析版本数据库{last_db_name}")
            if not self.__download_database(params, last_db_name):
                logger.info("下载全量数据库失败将重新生成，本次分析将只分析增量部分")
            elif os.path.exists(last_db_path):
                shutil.copyfile(last_db_path, db_path)
            else:
                logger.error("下载失败，本次将只分析增量文件，建议全量分析下项目。")
            diffs = SCMMgr(params).get_scm_diff()
            # 增量需要所有增量文件都重新生成，故这里不能过滤文件
            toscans = [diff.path.replace(os.sep, "/") for diff in diffs if diff.path.endswith(tuple(want_suffix))]
            toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
            if not toscans:
                return []
            with open(file_list, "w") as wf:
                for toscan in toscans:
                    wf.writelines(toscan)
                    wf.write("\n")
            inc_build_cmd = self.get_cmd(
                "Zeus",
                [
                    "inc_compile",
                    "-l",
                    lang,
                    "-p",
                    db_name,
                    "-db",
                    db_dir,
                    "-s",
                    source_dir,
                    # "-d",
                    "-f",
                    file_list,
                ],
            )
            # logger.info(" ".join(inc_build_cmd))
            # cmd_args += toscans
            sp = SubProcController(
                command=inc_build_cmd,
                cwd=ZEUS_HOME,
                stdout_line_callback=subprocc_log,
                stderr_line_callback=subprocc_log,
            )
            sp.wait()
            logger.info(sp.returncode)
            self.__upload_database(params, db_name)
            return
        # 全量编译命令
        toscans = [
            path.replace(os.sep, "/") for path in PathMgr().get_dir_files(source_dir, want_suffix=tuple(want_suffix))
        ]
        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)
        if not toscans:
            return []
        with open(file_list, "w") as wf:
            for toscan in toscans:
                wf.writelines(toscan)
                wf.write("\n")
        full_build_cmd = self.get_cmd(
            "Zeus",
            [
                "compile",
                "-p",
                db_name,
                "-cc",
                db_dir,
                "-l",
                lang,
                "-s",
                source_dir,
                "-f",
                file_list
                # "-d",  # 调试使用
            ],
        )
        # logger.info(" ".join(full_build_cmd))
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
        """
        tca ql 工具分析函数
        :param params: 执行需要的参数
        :return :
        """
        source_dir = params.source_dir
        relpos = len(source_dir) + 1
        work_dir = params.work_dir
        db_dir = os.path.join(work_dir, "db")
        repo_id = params.repo_id
        envs = os.environ
        HADES_HOME = envs.get("HADES_HOME", None)
        scm_revision = params["scm_revision"]
        version = self.__get_zeus_version(params)
        db_name = f"{repo_id}_{scm_revision}_{lang}_{version}"
        db_path = os.path.join(db_dir, f"{db_name}.db")
        if not os.path.exists(db_path):
            if not os.path.exists(db_dir):
                os.makedirs(db_dir)
            logger.info(f"本地未找到数据库文件{db_path}，从文件服务器下载")
            if not self.__download_database(params, db_name):
                logger.info("本地没有找到数据库，缓存数据库下载失败，可能分析文件为空")
                return []
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
                path.replace(os.sep, "/")[relpos:]
                for path in PathMgr().get_dir_files(source_dir, want_suffix=tuple(want_suffix))
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
        analyze_cmd = self.get_cmd(
            "Hades",
            [
                "analyze",
                "-l",
                lang,
                "-cc",
                db_dir,
                "-db",
                db_name,
                "-o",
                output_json,
                "-c",
                setting_file,
                # "-d",
            ],
        )
        # logger.info(" ".join(analyze_cmd))
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
        # if os.path.exists(db_path):
        #     self.__upload_database(params, db_name)
        return issues

    def get_cmd(self, tool_path, args):
        return __lu__().format_cmd(tool_path, args)


tool = TcaQl

if __name__ == "__main__":
    pass
