# TCA Server

## 工程结构
TCA Server由Main、Analysis、Login、File、ScmProxy五个微服务组成，主要技术栈为Django+uwsgi+nginx

## 配置说明

注意：以下配置内容可以参考 [config.sh](https://github.com/Faberiii/CodeAnalysis/blob/main/server/scripts/config.sh)文件进行查阅，使用时主要关注 MySQL、Redis 的配置，其他配置均已提供默认值，可以根据需要进行调整

### Main服务
框架配置：

- MAIN_DEBUG_MODE: Main服务的Debug模式，``true/false``
- MAIN_SECRET_KEY: Main服务的Secret Key配置，可以通过``from django.core.management.utils import get_random_secret_key;get_random_secret_key()``方法获取

Main服务DB配置：

- MAIN_DB_NAME：Main服务的数据库名称
- MAIN_DB_USER：Main服务的数据库用户名
- MAIN_DB_PASSWORD：Main服务的数据库密码
- MAIN_DB_HOST：Main服务的数据库地址
- MAIN_DB_PORT：Main服务的数据库端口号

Main服务Redis配置：

- MAIN_REDIS_HOST：Main服务访问的Redis地址
- MAIN_REDIS_PORT：Main服务访问的Redis端口号
- MAIN_REDIS_PASSWD：Main服务访问的Redis密码
- MAIN_REDIS_DBID：Main服务访问的Redis DB编号，默认为1（Analysis服务默认访问0号DB）

服务交互配置：
- MAIN_SENTRY_DSN：Main服务异常日志上报至sentry配置
- PASSWORD_KEY：数据加密密钥
- API_TICKET_SALT：服务访问Token加密密钥
- API_TICKET_TOKEN：服务访问Token
- FILE_SERVER_TOKEN：文件服务器访问Token
- CODEDOG_TOKEN：CodeDog默认访问的Token


### Analysis服务
框架配置：

- ANALYSIS_DEBUG_MODE: Analysis服务的Debug模式，``true/false``
- ANALYSIS_SECRET_KEY: Analysis服务的Secret Key配置，可以通过``from django.core.management.utils import get_random_secret_key;get_random_secret_key()``方法获取

Analysis服务DB配置：

- ANALYSIS_DB_NAME：Analysis服务的数据库名称
- ANALYSIS_DB_USER：Analysis服务的数据库用户名
- ANALYSIS_DB_PASSWORD：Analysis服务的数据库密码
- ANALYSIS_DB_HOST：Analysis服务的数据库地址
- ANALYSIS_DB_PORT：Analysis服务的数据库端口号

Analysis服务Redis配置：

- ANALYSIS_REDIS_HOST：Analysis服务访问的Redis地址
- ANALYSIS_REDIS_PORT：Analysis服务访问的Redis端口号
- ANALYSIS_REDIS_PASSWD：Analysis服务访问的Redis密码
- ANALYSIS_REDIS_DBID：Analysis服务访问的Redis DB编号，默认为0（Main服务默认访问1号DB）

服务交互配置：
- ANALYSIS_SENTRY_DSN：Analysis服务异常日志上报至sentry配置
- PASSWORD_KEY：数据加密密钥
- API_TICKET_SALT：服务访问Token加密密钥
- API_TICKET_TOKEN：服务访问Token


### Login服务
框架配置：

- LOGIN_DEBUG_MODE: Login服务的Debug模式，``true/false``
- LOGIN_SECRET_KEY: Login服务的Secret Key配置，可以通过``from django.core.management.utils import get_random_secret_key;get_random_secret_key()``方法获取

Login服务DB配置：

- LOGIN_DB_NAME：Login服务的数据库名称
- LOGIN_DB_USER：Login服务的数据库用户名
- LOGIN_DB_PASSWORD：Login服务的数据库密码
- LOGIN_DB_HOST：Login服务的数据库地址
- LOGIN_DB_PORT：Login服务的数据库端口号

服务交互配置：
- PASSWORD_KEY：数据加密密钥
- API_TICKET_SALT：服务访问Token加密密钥
- API_TICKET_TOKEN：服务访问Token

注：配置文件中的pub_key与private_key生成方式可以参考以下方法：
```bash
$ ssh-keygen -t rsa -b 1024 -m PEM -f tca_login.key
$ openssl rsa -in tca_login.key -pubout -outform PEM -out tca_login.key.pub
$ cat tca_login.key  # 作为private_key的内容
$ cat tca_login.key.pub  # 作为pub_key的内容
```

### File服务
框架配置：

- FILE_DEBUG_MODE: File服务的Debug模式，``true/false``
- FILE_SECRET_KEY: File服务的Secret Key配置，可以通过``from django.core.management.utils import get_random_secret_key;get_random_secret_key()``方法获取

File服务DB配置：

- FILE_DB_NAME：File服务的数据库名称
- FILE_DB_USER：File服务的数据库用户名
- FILE_DB_PASSWORD：File服务的数据库密码
- FILE_DB_HOST：File服务的数据库地址
- FILE_DB_PORT：File服务的数据库端口号

服务交互配置：
- FILE_SENTRY_DSN：File服务异常日志上报至sentry配置
- API_TICKET_SALT：服务访问Token加密密钥
- API_TICKET_TOKEN：服务访问Token

File存储引擎配置
- FILE_STORAGE_CLIENT: 文件存储引擎，可选项：``LOCAL``/``MINIO``/``COS``
    - 当配置引擎为``LOCAL``，可以指定``FILE_STORAGE_DIR``文件存放的路径
    - 当配置引擎为``MINIO``，可以指定以下变量：
        - FILE_MINIO_ENTRYPOINT：MINIO服务地址
        - FILE_MINIO_ACCESS_KEY：MINIO服务访问账号
        - MINIO_SECRET_KEY：MINIO服务访问密码
    - 当配置引擎为``COS``，可以指定以下变量
        - TENCENT_COS_APPID
        - TENCENT_COS_SECRETID
        - TENCENT_COS_SECRETKEY
        - TENCENT_COS_REGION
        - TENCENT_COS_ROOT_BUCKET：填写格式为bucket-appid

### ScmProxy
服务配置：
- SCMPROXY_HOST：ScmProxy服务的HOST，默认为``0.0.0.0``
- SCMPROXY_PORT：ScmProxy服务监听端口，默认为``8009``
- SCMPROXY_SENTRY_URL：ScmProxy服务异常日志上报至sentry配置
- SCMPROXY: 通过本环境变量去指定其他服务调用ScmProxy服务的地址，默认值为``127.0.0.1:8009``
