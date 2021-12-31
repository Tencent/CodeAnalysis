# 接口调用说明

## 接口地址

http://{host}/server/
注：host 指当前浏览器访问该文档的 URL 域名部分。

## 接口鉴权方式

发起请求时，需要在头部中添加以下格式形式，对应的 value 请看下面获取方式

```json
{
  "TCA-USERID": "{当前user-id，比如xiaoming}",
  "TCA-TIMESTAMP": "{当前时间戳，比如1614565593}",
  "TCA-TICKET": "{当前user的token}"
}
```
获取 user_id 和 token 位置：
![](../images/API的个人令牌.png)

计算 带 TCA-TICKET 的头部方式(以 Python 代码为例):

```python
from time import time
from hashlib import sha256

def get_headers(user_id, token):
    timestamp = int(time())
    token_sig = "%s%s#%s#%s%s" % (timestamp, user_id, token, user_id, timestamp)
    ticket = sha256(token_sig.encode("utf-8")).hexdigest().upper()
    return {
        "TCA-USERID": user_id,
        "TCA-TIMESTAMP": str(timestamp),
        "TCA-TICKET": ticket
    }
```

## 获取 org_sid 和 project_team 信息

通过平台访问具体代码库扫描情况时，可从 URL 中获取对应 org_sid 和 project_team 字段，查看方式如下例子：

代码库扫描地址：http://{host}/t/xxx/p/yyy/code-analysis/repos/1/projects?limit=10&offset=0

其中，org_sid 为`xxx`字段，project_team 为 `yyy`字段

## Example

```python
import requests
# 假设：
# 当前域名为http://tca.com/，当前org_sid为helloworld
# 获取helloworld团队下的hellotca项目下登记的代码库
url="http://tca.com/server/main/api/orgs/helloworld/teams/hellotca/repos/?limit=12&offset=0"
headers = {
  "TCA-USERID": user_id,
  "TCA-TIMESTAMP": str(timestamp),
  "TCA-TICKET": ticket
}

response = requests.get(url, headers=headers)
print(response.json())
# 结果如下：
{
    "data": {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "id": 23,
                "name": "repo_name",
                "scm_url": "http://git.repo.com/group/repo_name",
                "scm_type": "git",
                "branch_count": 1,
                "scheme_count": 1,
                "job_count": 1,
                "created_time": "2021-05-14 02:34:44.509118+00:00",
                "recent_active": {
                    "id": 27,
                    "branch_name": "master",
                    "active_time": "2021-05-14 02:34:44.509118+00:00",
                    "total_line_num": 1,
                    "code_line_num": 1
                },
                "created_from": "tca",
                "creator": {
                    "username": "author",
                    "nickname": "author",
                    "status": 1,
                    "avatar": "url",
                    "org": "org_name"
                },
                "symbol": null,
                "scm_auth": {
                    "id": 1,
                    "scm_account": null,
                    "scm_oauth": null,
                    "scm_ssh": {
                        "id": 1,
                        "name": "test",
                        "scm_platform": 2,
                        "scm_platform_desc": null,
                        "user": {
                            "username": "username",
                            "nickname": "nickname",
                            "status": 1,
                            "avatar": "url",
                            "org": "org_name"
                        }
                    },
                    "auth_type": "ssh_token",
                    "created_time": "2021-05-14T10:34:44.552859+08:00",
                    "modified_time": "2021-05-14T10:34:44.552887+08:00"
                },
                "project_team": {
                    "name": "test",
                    "display_name": "测试",
                    "status": 1,
                    "org_sid": "test"
                }
            }
        ]
    },
    "code": 0,
    "msg": "请求成功",
    "status_code": 200
}
```

## 分页方式

平台返回的数据分页格式是使用`limit`和`offset`参数进行分页处理

比如：`server/main/api/orgs/<org_sid>/teams/?limit=12&offset=12`获取得到的数据是从第 13 条开始获取
