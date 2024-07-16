# API调用脚本使用指引

## 操作步骤
#### 1. 修改脚本api_invoke.py的内部参数，填写个人令牌mytoken
#### 2. 部署代码分析服务
#### 3. 进入项目根目录
#### 4. 检查requests 模块是否安装，如未安装，可执行下列安装指令。
```bash
pip install requests
```
#### 5. 设置参数method，选择要执行的api接口，并根据接口添加所需参数。
#### 6. 执行脚本python ScriptsAPI.py

## 方法总览

| method                 | 类型                  |
|------------------------|---------------------|
| create_repository      | 创建代码库               |
| update_scheme_settings | 设置指定代码库的指定方案的代码度量配置 |
| create_project         | 创建分析项目              |
| create_scans           | 启动任务                |
| get_scan_cons          | 轮询任务结果              |
| get_overview           | 获取分析概览              |
| get_issues             | 查看扫描问题列表            |
| get_issue_detail       | 查看问题详情              |
| get_ccissues           | 查看指定项目的圈复杂度问题列表     |
|  get_dupfiles          | 查看指定项目的重复文件列表       |


## API详细信息


### 一、创建代码库
#### 1. url请求
```
POST /server/main/api/orgs/<org_sid>/teams/<team_name>/repos/
```
#### 2. 参数说明
##### 脚本参数

| 字段        | 类型  | 描述                       |
|-----------|-----|--------------------------|
| method    | str | 调用的方法名，create_repository |
| base_url  | str | 基础路径                     |
| org_sid   | str | 项目组名称                    |
| team_name | str | 团队唯一标识                   |
| scm_url   | str | 代码库地址                    |
|  scm_type | str | 填git或svn                 |

##### 脚本内部参数
| Key           | 类型  | Value                |
|---------------|-----|----------------------|
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=create_repository --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --scm_url=${TCA_SCM_URL} --scm_type=${TCA_SCM_TYPE}
```


### 二、设置指定代码库的指定方案的代码度量配置
#### 1. url请求
```
PUT /server/main/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/schemes/<scheme_id>/metricconf/
```
#### 2. 参数说明
##### 脚本参数

| 字段        | 类型  | 描述                       |
|-----------|-----|--------------------------|
| method    | str | 调用的方法名，update_scheme_settings |
| base_url  | str | 基础路径                     |
| org_sid   | str | 项目组名称                    |
| team_name | str | 团队唯一标识                   |
| repo_id   | str | 代码库id                    |
| scheme_id | str | 扫描方案id                   |

##### 脚本内部参数
| Key           | 类型  | Value                |
|---------------|-----|----------------------|
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=update_scheme_settings --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --scheme_id=${TCA_SCHEME_ID}
```



### 三、创建分析项目
#### 1. url请求
```
POST /server/main/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/
```
#### 2. 参数说明
##### 脚本参数

| 字段               | 类型  | 描述                                    |
|------------------|-----|---------------------------------------|
| method           | str | 调用的方法名，create_repository              |
| base_url         | str | 基础路径                                  |
| org_sid          | str | 项目组名称                                 |
| team_name        | str | 团队唯一标识                                |
| repo_id          | str | 代码库id                                 |
| scan_scheme_id   | int | 和global_scheme_id二选一进行填写，当前代码库的扫描方案编号 |
| global_scheme_id | int | 和scan_scheme_id二选一进行填写，扫描方案模板编号       |
| branch           | str | 分支                                    |


##### 脚本内部参数
| Key           | 类型  | Value                |
|---------------|-----|----------------------|
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=create_project --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --scan_scheme_id=${TCA_SCAN_SCHEME_ID} --branch=${TCA_BRANCH}
```


### 四、启动任务
#### 1. url请求
```
POST /server/main/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/scans/create/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                       |
|------------|-----|--------------------------|
| method     | str | 调用的方法名，create_scans |
| base_url   | str | 基础路径                     |
| org_sid    | str | 项目组名称                    |
| team_name  | str | 团队唯一标识                   |
| repo_id    | str | 代码库id                    |
| project_id | str | 分析项目id                   |


##### 脚本内部参数
| Key           | 类型  | Value                |
|---------------|-----|----------------------|
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=create_scans --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID}
```



### 五、轮询任务结果
#### 1. url请求
```
GET /server/main/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/jobs/<job_id>/detail/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                       |
|------------|-----|--------------------------|
| method     | str | 调用的方法名，get_scan_cons |
| base_url   | str | 基础路径                     |
| org_sid    | str | 项目组名称                    |
| team_name  | str | 团队唯一标识                   |
| repo_id    | str | 代码库id                    |
| project_id | str | 分析项目id                   |

##### 脚本内部参数
| Key | 类型   | Value |
|--|------| - |
| Authorization | str  | "Token 当前user的token" |
| sleeptime | int  | 轮询间隔的时间 |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_scan_cons --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID} --job_id=${TCA_JOB_ID}
```


### 六、获取分析概览
#### 1. url请求
```
GET /server/analysis/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/overview/
```
#### 2. 参数说明
##### 脚本参数

| 字段          | 类型  | 描述                  |
|-------------|-----|---------------------|
| method      | str | 调用的方法名，get_overview |
| base_url    | str | 基础路径                |
| org_sid     | str | 项目组名称               |
| team_name   | str | 团队唯一标识              |
| repo_id     | str | 代码库id               |
| project_id  | str | 分析项目id              |

##### 脚本内部参数
| Key | 类型  | Value |
|--|-----| - |
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_overview --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID}
```



### 七、查看扫描问题列表
#### 1. url请求
```
GET /server/analysis/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codelint/issues/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                |
|------------|-----|-------------------|
| method     | str | 调用的方法名，get_issues |
| base_url   | str | 基础路径              |
| org_sid    | str | 项目组名称             |
| team_name  | str | 团队唯一标识            |
| repo_id    | str | 代码库id             |
| project_id | str | 分析项目id            |

##### 脚本内部参数
| Key | 类型  | Value |
|--|-----| - |
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_issues --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID}
```


### 八、查看问题详情
#### 1. url请求
```
GET /server/analysis/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codelint/issues/<issue_id>/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                      |
|------------|-----|-------------------------|
| method     | str | 调用的方法名，get_issue_detail |
| base_url   | str | 基础路径                    |
| org_sid    | str | 项目组名称                   |
| team_name  | str | 团队唯一标识                  |
| repo_id    | str | 代码库id                   |
| project_id | str | 分析项目id                  |
|  issue_id  | str | 问题id                    |

##### 脚本内部参数
| Key | 类型  | Value |
|--|-----| - |
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_issue_detail --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID} --issue_id=${TCA_ISSUE_ID}
```


### 九、查看指定项目的圈复杂度问题列表
#### 1. url请求
```
GET /server/analysis/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codemetric/ccissues/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                  |
|------------|-----|---------------------|
| method     | str | 调用的方法名，get_ccissues |
| base_url   | str | 基础路径                |
| org_sid    | str | 项目组名称               |
| team_name  | str | 团队唯一标识              |
| repo_id    | str | 代码库id               |
| project_id | str | 分析项目id              |

##### 脚本内部参数
| Key | 类型  | Value |
|--|-----| - |
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_ccissues --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID}
```



### 十、查看指定项目的重复文件列表
#### 1. url请求
```
GET /server/analysis/api/orgs/<org_sid>/teams/<team_name>/repos/<repo_id>/projects/<project_id>/codemetric/dupfiles/
```
#### 2. 参数说明
##### 脚本参数

| 字段         | 类型  | 描述                   |
|------------|-----|----------------------|
| method     | str | 调用的方法名，get_dupfiles  |
| base_url   | str | 基础路径                 |
| org_sid    | str | 项目组名称                |
| team_name  | str | 团队唯一标识               |
| repo_id    | str | 代码库id                |
| project_id | str | 分析项目id               |

##### 脚本内部参数
| Key | 类型  | Value |
|--|-----| - |
| Authorization | str | "Token 当前user的token" |

#### 3. 操作示例
```bash
python ScriptsAPI.py --base_url=${TCA_BASE_URL} --method=get_dupfiles --org_sid=${TCA_ORG_SID} --team_name=${TCA_TEAM_NAME} --repo_id=${TCA_REPO_ID} --project_id=${TCA_PROJECT_ID}
```




