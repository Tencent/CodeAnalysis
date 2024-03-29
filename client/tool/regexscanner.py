# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

""" regexscanner 正则匹配分析工具
"""

import os
import sys
import yaml
import shutil
import json

from node.app import settings
from task.codelintmodel import CodeLintModel
from task.scmmgr import SCMMgr
from util.pathlib import PathMgr
from util.textutil import CODE_EXT
from task.basic.datahandler.filter import REVISION_FILTER, PATH_FILTER
from util.configlib import ConfigReader
from util.exceptions import AnalyzeTaskError
from util.pathfilter import FilterPathUtil
from util.subprocc import SubProcController
from task.authcheck.check_license import __lu__
from util.logutil import LogPrinter

logger = LogPrinter


class RegexScanner(CodeLintModel):
    def __init__(self, params):
        CodeLintModel.__init__(self, params)
        self.tool_home = os.environ.get("REGEXSCANNER_HOME")
        self.tool_name = self.__class__.__name__

    def __add_rules(self, work_dir, rules):
        """添加yaml规则文件
        """
        rules_path = os.path.join(self.tool_home, "rules")
        relpos = len(rules_path) + 1
        endsuff = [".yaml", ".yml"]
        filelist = []
        for dirpath, _, files in os.walk(rules_path):
            for filename in files:
                if filename.lower().endswith(tuple(endsuff)):
                    filelist.append(os.path.join(dirpath, filename))
        config_rules_path = os.path.join(work_dir, "config_rules")
        if os.path.exists(config_rules_path):
            shutil.rmtree(config_rules_path)
        os.mkdir(config_rules_path)
        for single_file in filelist:
            rel_path = single_file[relpos:]
            file_path = os.path.join(config_rules_path, rel_path)
            with open(single_file,'r') as fp:
                data = yaml.safe_load(fp)
            if data:
                if data.__contains__('rules'):
                    for rule_data in data['rules']:
                        if rule_data["name"] in rules:
                            if not os.path.exists(os.path.dirname(file_path)):
                                os.makedirs(os.path.dirname(file_path))
                            shutil.copy(single_file, file_path)
                            break
        return config_rules_path

    def __get_regexes_exp(self, regex_type, rule_params_dict):
        """获取正则列表
        """
        regexes = []
        i = 1
        while True:
            key = f"{regex_type}{i}"
            if key in rule_params_dict:
                reg_exp = rule_params_dict.get(key, "")
                if reg_exp:
                    regexes.append(reg_exp)
                i += 1
            else:
                return regexes

    def __format_rules(self, work_dir, rule_list):
        """格式化规则
        """
        rules = {"rules": []}
        no_params_rules = []
        for rule in rule_list:
            rule_name = rule['name']
            if not rule.get('params'):
                logger.error(f"{rule_name} rule parameter is empty, check for existing rules.")
                rules["rules"].append({"name":rule_name})
                no_params_rules.append(rule_name)
                continue
            if "[regexcheck]" in rule['params']:
                rule_params = rule['params']
            else:
                rule_params = "[regexcheck]\r\n" + rule['params']
            rule_params_dict = ConfigReader(cfg_string=rule_params).read('regexcheck')

            regex = rule_params_dict.get("regex", "")
            regex_not = rule_params_dict.get("regex_not", "")
            if not regex:
                rules["rules"].append({"name":rule_name})
                continue
            regexes = self.__get_regexes_exp("regex", rule_params_dict)
            regexes_not = self.__get_regexes_exp("regex_not", rule_params_dict)

            # 规则的过滤路径（正则表达式）
            exclude_paths = rule_params_dict.get('exclude', '')
            exclude_paths = [p.strip() for p in exclude_paths.split(';') if p.strip()] if exclude_paths else []
            include_paths = rule_params_dict.get('include', '')
            include_paths = [p.strip() for p in include_paths.split(';') if p.strip()] if include_paths else []

            # 大小写不敏感,可以支持True|true|False|false等
            ignore_comment = True if rule_params_dict.get('ignore_comment', 'False').lower() == 'true' else False
            file_scan = True if rule_params_dict.get('file_scan', 'False').lower() == 'true' else False
            msg = rule_params_dict.get('msg', "Irregular codes found: %s")
            match_group = rule_params_dict.get('match_group', 0)
            entropy = rule_params_dict.get('entropy', 0.0)
            rule = {
                "name": rule_name,
                "regex": regex,
                "regexes": regexes,
                "regex-not": regex_not,
                "regexes-not": regexes_not,
                "message": msg,
                "ignore-comment": ignore_comment,
                "filescan": file_scan,
                "severity": "error",
                "excludes": exclude_paths,
                "includes": include_paths,
                "match-group": match_group,
                "entropy": entropy,
            }
            rules["rules"].append(rule)
        config_rules_path = self.__add_rules(work_dir, no_params_rules)
        rules_path = os.path.join(config_rules_path, "regexscanner_rules.yaml")
        with open(rules_path, "w", encoding="utf-8") as f:
            yaml.dump(rules, f)
        return config_rules_path

    def analyze(self, params):
        '''执行regexscanner分析任务
        :param params: 需包含下面键值：
           'rules'： lint分析的规则列表
           'incr_scan' : 是否增量分析
        :return: return a :py:class:`IssueResponse`
        '''
        source_dir = params['source_dir']
        work_dir = params['work_dir']
        incr_scan = params['incr_scan']
        rules = params["rules"]

        files_path = os.path.join(work_dir, "regexscanner_paths.txt")
        output_path = os.path.join(work_dir, "regexscanner_result.json")

        toscans = []
        if incr_scan:
            diffs = SCMMgr(params).get_scm_diff()
            toscans = [os.path.join(source_dir, diff.path) for diff in diffs if diff.state != 'del']
        else:
            toscans = PathMgr().get_dir_files(source_dir)

        # filter include and exclude path
        relpos = len(source_dir) + 1
        toscans = FilterPathUtil(params).get_include_files(toscans, relpos)

        toscans = self.get_valid_encode_files(toscans)

        if not toscans:
            logger.debug("To-be-scanned files is empty ")
            return []
        logger.debug("files to scan: %d" % len(toscans))
        with open(files_path, "w", encoding="UTF-8") as f:
            f.write("\n".join(toscans))

        # 写入规则
        config_rules_path = self.__format_rules(work_dir, params['rule_list'])

        # 执行分析工具
        options = [
            "--filelist=%s" % files_path,
            "--project-root=%s" % source_dir,
            "--ruleset=%s" % config_rules_path,
            "--output-format=json",
            "--output=%s" % output_path,
        ]
        scan_cmd = self.get_cmd(options)
        logger.info(f"scan_cmd: {' '.join(scan_cmd)}")

        subproc = SubProcController(
            scan_cmd, stdout_line_callback=logger.info, stderr_line_callback=logger.info)
        subproc.wait()

        if not os.path.exists(output_path):
            logger.info("No results file generated.")
            raise AnalyzeTaskError("Tool running error")

        issues = []
        with open(output_path, "r") as f:
            outputs_data = json.load(f)
            if not outputs_data:
                return []
        for item in outputs_data:
            if item["rule"] not in rules:
                continue
            issue = dict()
            issue["path"] = item["path"]
            issue["line"] = item.get("start-line") if "start-line" in item else item["line"]
            issue["column"] = item.get("start-column") if "start-column" in item else item["column"]
            issue["msg"] = item["msg"]
            issue["rule"] = item["rule"]
            issue["refs"] = []
            issues.append(issue)

        logger.debug(issues)
        return issues

    def get_cmd(self, args):
        tool_path = os.path.join(self.tool_home, "bin", settings.PLATFORMS[sys.platform], self.tool_name)
        if settings.PLATFORMS[sys.platform] == "windows":
            tool_path = f"{tool_path}.exe"
        return __lu__().format_cmd(tool_path, args)

    def get_valid_encode_files(self, toscans: list):
        """
        获取能正确解码的文件字符串
        """
        new_toscans = []
        for path in toscans:
            try:
                path.encode(encoding="UTF-8")
            except UnicodeEncodeError:
                logger.info("ignore file: %s" % path)
                continue
            new_toscans.append(path)
        return new_toscans

    def set_filter_type_list(self):
        '''
        通过覆盖该函数来选择过滤类型
        目前存在的过滤类型有：
        1. NO_FILTER  不需要过滤
        2. DIFF_FILTER 将非修改的代码文件进行过滤
        3. REVISION_FILTER 通过起始版本号进行过滤
        4. PATH_FILTER 通过用户设置的黑白名单进行过滤
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        '''
        # 已经过滤文件和diff增量,不需要重复过滤,只需要根据revision过滤
        return [REVISION_FILTER, PATH_FILTER]


tool = RegexScanner

if __name__ == '__main__':
    pass
