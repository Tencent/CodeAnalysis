# CLS使用文档
CLS(Common License Server)是TCA自研工具的License鉴权服务。

## 准备
1. 一台CLS服务专属机器，CLS服务需要跟该机器绑定

## 部署
1. 在CLS目录下执行以下命令，获取Server ID和client License
```shell
$ ./cls server
2022-04-13 18:35:29.356510559 +0800 CST [INFO] Version: 20220328.1
2022-04-13 18:35:29.44083463 +0800 CST [INFO] The client license is:
xxx
2022-04-13 18:35:29.454552966 +0800 CST [INFO] License Server ID: xxx
```
- Server ID: 机器码，用于跟TCA团队申请License授权
- client License: 提供给TCA Client, 方便TCA Client进行工具鉴权
2. 跟TCA团队邮件申请License

- 发送邮箱：
```
v_cocohwang@tencent.com
anjingliu@tencent.com
yalechen@tencent.com
tommyzhang@tencent.com
```

- 格式如下：

TCA自研工具License申请邮件

| |  |
|  :----:  | :----:  |
| 申请人名称  | xxx |
| 申请人所在公司/学校名称 | xxx |
| 申请人邮箱 | xxx |
| 申请人手机号码 | xxx |
| 首次登记的机器码 | xxx |
| 体验申请用途 | xxx |

3. 收到TCA团队回复邮件之后，在CLS目录下的[config.yaml](server/cls/config.yaml)文件中填写License
4. 执行以下命令启动
```shell
./cls server -d
```

## 高级
### 自动重启
```shell
# 查找CLS进程ID
ps aux|grep cls
# 重启服务
kill -USR2 <pid>
```
