# TCA Client 客户端配置与使用

## 安装Python环境和第三方库
1. 预装Python3.7、pip，支持 `python3` 和 `pip3` 命令 
2. 安装依赖：`pip3 install -r client/requirements/app_reqs.pip`

## 安装第三方工具
1. 进入到`client/requirements`目录
2. 在命令行中执行安装脚本`install.sh`(linux/mac环境)或`install.bat`(windows环境)

## 配置client/config.ini文件
将`<Server IP地址>`替换成实际的serve ip（可包含端口号）。

## 配置client/codedog.ini文件
1. 填写以下必填项：`token`,`org_sid`,`team_name`,`source_dir`
- 各字段获取方式，详见根目录下文档`《GettingStart(TCA快速入门).pdf》`
2. 按需填写其他可选项，也可以不填，按默认配置执行

## 启动代码分析
1. 进入到`client`目录下
2. 执行命令：`python3 codepuppy.py localscan`