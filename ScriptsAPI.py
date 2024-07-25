# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
API调用脚本
"""

import logging
import requests
import argparse
from time import sleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# 填写代码分析账户的token
my_token = "mytoken"
sleep_time = 5


class ScriptsAPI():
    def __init__(self, my_token, sleep_time):
        self.my_token = my_token
        self.sleep_time = sleep_time

    def add_arguments(self, parser):
        parser.add_argument('--method', type=str, help='Set method')
        parser.add_argument('--base_url', type=str, help='Set base_url')
        parser.add_argument('--org_sid', type=str, help='Set org_sid')
        parser.add_argument('--team_name', type=str, help='Set team_name')

        # 选填路径参数
        parser.add_argument('--repo_id', type=str, help='Set repo_id', default=None)
        parser.add_argument('--scheme_id', type=str, help='Set scheme_id', default=None)
        parser.add_argument('--project_id', type=str, help='Set project_id', default=None)
        parser.add_argument('--issue_id', type=str, help='Set issue_id', default=None)
        parser.add_argument('--job_id', type=str, help='Set job_id', default=None)

        # 创建代码库相关参数
        parser.add_argument('--scm_url', type=str, help='Set scm_url', default=None)
        parser.add_argument('--scm_type', type=str, help='Set scm_type', default=None)

        # 创建分析项目相关参数
        parser.add_argument('--scan_scheme_id', type=int, help='Set scan_scheme_id', default=None)
        parser.add_argument('--global_scheme_id', type=int, help='Set global_scheme_id', default=None)
        parser.add_argument('--branch', type=str, help='Set branch', default=None)

    def handle(self, options):
        if options['method'] is None:
            logger.error("method 不能为空！")
            return
        if options['base_url'] is None:
            logger.error("base_url 不能为空！")
            return
        if options['org_sid'] is None:
            logger.error("org_sid 不能为空！")
            return
        if options['team_name'] is None:
            logger.error("team_name 不能为空！")
            return
        method = options['method']
        base_url = options['base_url']
        org_sid = options['org_sid']
        team_name = options['team_name']

        if method == 'create_repository':
            # 1、创建代码库
            self.create_repository_preproccess(base_url, org_sid, team_name, options)
        elif method == 'update_scheme_settings':
            # 2、设置指定代码库的指定方案的代码度量配置
            self.update_scheme_settings_preproccess(base_url, org_sid, team_name, options)
        elif method == 'create_project':
            # 3、创建分析项目
            self.create_project_preproccess(base_url, org_sid, team_name, options)
        elif method == 'create_scans':
            # 4、启动任务
            self.create_scans_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_scan_cons':
            # 5、轮询任务结果
            self.get_scan_cons_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_overview':
            # 6、获取分析概览
            self.get_overview_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_issues':
            # 7、查看扫描问题列表
            self.get_issues_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_issue_detail':
            # 8、查看问题详情
            self.get_issue_detail_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_ccissues':
            # 9、查看指定项目的圈复杂度问题列表
            self.get_ccissues_preproccess(base_url, org_sid, team_name, options)
        elif method == 'get_dupfiles':
            # 10、查看指定项目的重复文件列表
            self.get_dupfiles_preproccess(base_url, org_sid, team_name, options)
        else:
            logger.error("不存在该方法，请重新执行！")
            return

    def create_repository_preproccess(self, base_url, org_sid, team_name, options):
        # 请求体必填字段判断
        if options['scm_url'] is None:
            logger.error("scm_url 不能为空！")
            return
        if options['scm_type'] is None:
            logger.error("scm_type 不能为空！")
            return
        if options['scm_type'] not in ['git', 'svn']:
            logger.error("scm_type 必须是git或svn！")
            return

        payload = {}
        payload.update({'scm_url': options['scm_url']})
        payload.update({'scm_type': options['scm_type']})

        self.create_repository(base_url, org_sid, team_name, payload)

    def update_scheme_settings_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['scheme_id'] is None:
            logger.error("scheme_id 不能为空！")
            return
        scheme_id = options['scheme_id']

        self.update_scheme_settings(base_url, org_sid, team_name, repo_id, scheme_id)

    def create_project_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']

        # 请求体必填字段判断
        payload = {}
        if options['scan_scheme_id'] is None and options['global_scheme_id'] is None:
            logger.error("scan_scheme_id和global_scheme_id字段不能全部为空！")
            return
        if options['scan_scheme_id'] and options['global_scheme_id']:
            logger.error("scan_scheme_id和global_scheme_id字段不能同时填入！")
            return
        if options['scan_scheme_id']:
            payload.update({'scan_scheme_id': options['scan_scheme_id']})
        if options['global_scheme_id']:
            payload.update({'global_scheme_id': options['global_scheme_id']})

        if options['branch'] is None:
            logger.error("branch 不能为空！")
            return
        payload.update({'branch': options['branch']})

        self.create_project(base_url, org_sid, team_name, repo_id, payload)

    def create_scans_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']

        self.create_scans(base_url, org_sid, team_name, repo_id, project_id)

    def get_scan_cons_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']
        if options['job_id'] is None:
            logger.error("job_id 不能为空！")
            return
        job_id = options['job_id']

        self.get_scan_cons(base_url, org_sid, team_name, repo_id, project_id, job_id)

    def get_overview_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']

        self.get_overview(base_url, org_sid, team_name, repo_id, project_id)

    def get_issues_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']

        self.get_issues(base_url, org_sid, team_name, repo_id, project_id)

    def get_issue_detail_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']
        if options['issue_id'] is None:
            logger.error("issue_id 不能为空！")
            return
        issue_id = options['issue_id']

        self.get_issue_detail(base_url, org_sid, team_name, repo_id, project_id, issue_id)

    def get_ccissues_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']

        self.get_ccissues(base_url, org_sid, team_name, repo_id, project_id)

    def get_dupfiles_preproccess(self, base_url, org_sid, team_name, options):
        if options['repo_id'] is None:
            logger.error("repo_id 不能为空！")
            return
        repo_id = options['repo_id']
        if options['project_id'] is None:
            logger.error("project_id 不能为空！")
            return
        project_id = options['project_id']

        self.get_dupfiles(base_url, org_sid, team_name, repo_id, project_id)

    def create_repository(self, base_url, org_sid, team_name, payload):
        logger.info("创建代码库")

        url = f"{base_url}server/main/api/orgs/{org_sid}/teams/{team_name}/repos/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.text)

    def update_scheme_settings(self, base_url, org_sid, team_name, repo_id, scheme_id):
        logger.info("设置指定代码库的指定方案的代码度量配置")

        url = f"{base_url}server/main/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/schemes/{scheme_id}/metricconf/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("PUT", url, headers=headers)
        logger.info(response.text)

    def create_project(self, base_url, org_sid, team_name, repo_id, payload):
        logger.info("创建分析项目")

        url = f"{base_url}server/main/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        logger.info(response.text)

    def create_scans(self, base_url, org_sid, team_name, repo_id, project_id):
        logger.info("启动分析任务")

        url = f"{base_url}server/main/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/scans/create/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("POST", url, headers=headers)
        logger.info(response.text)

    def get_scan_cons(self, base_url, org_sid, team_name, repo_id, project_id, job_id):
        logger.info("轮询任务结果")

        # 这里要做出一个轮询效果，循环判断状态
        url = f"{base_url}server/main/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/jobs/{job_id}/detail/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }

        while True:
            response = requests.request("GET", url, headers=headers)
            logger.info(response.text)
            if response.status_code != 200:
                logger.error("api执行失败，请检查输入的参数是否正确！")
                return
            data = response.json()
            if data['data']['state'] == 2:
                break
            sleep(self.sleep_time)

        logger.info("分析项目执行完毕，请查看分析结果！")

    def get_overview(self, base_url, org_sid, team_name, repo_id, project_id):
        logger.info("获取分析概览")

        url = f"{base_url}server/analysis/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/overview/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("GET", url, headers=headers)
        logger.info(response.text)

    def get_issues(self, base_url, org_sid, team_name, repo_id, project_id):
        logger.info("查看问题列表")

        url = f"{base_url}server/analysis/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/codelint/issues/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("GET", url, headers=headers)
        logger.info(response.text)

    def get_issue_detail(self, base_url, org_sid, team_name, repo_id, project_id, issue_id):
        logger.info("查看问题详情")

        url = f"{base_url}server/analysis/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/codelint/issues/{issue_id}/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("GET", url, headers=headers)
        logger.info(response.text)

    def get_ccissues(self, base_url, org_sid, team_name, repo_id, project_id):
        logger.info("查看指定项目的圈复杂度问题列表")

        url = f"{base_url}server/analysis/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/codemetric/ccissues/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("GET", url, headers=headers)
        logger.info(response.text)

    def get_dupfiles(self, base_url, org_sid, team_name, repo_id, project_id):
        logger.info("查看指定项目的重复文件列表")

        url = f"{base_url}server/analysis/api/orgs/{org_sid}/teams/{team_name}/repos/{repo_id}/projects/{project_id}/codemetric/dupfiles/"
        headers = {
            'Authorization': f'Token {self.my_token}'
        }
        response = requests.request("GET", url, headers=headers)
        logger.info(response.text)


scripts_api = ScriptsAPI(my_token, sleep_time)
parser = argparse.ArgumentParser(description='Add parameters required for the script invocation')
scripts_api.add_arguments(parser)
options = vars(parser.parse_args())
scripts_api.handle(options)
