# 基于MinIO部署文件服务器
TCA的``file``服务支持对接``MinIO``作为底层存储，将文件转发到已部署的MinIO平台上进行持久化存储

## 本地部署
> 注意：如果之前已经使用本地进行存储，切换为MinIO后，之前已经上传的文件只能到服务部署的目录``server/projects/file/data``查看，不支持通过页面进行下载

### 前置步骤
获取MinIO平台登录的账号密码，用于上传文件

### 配置步骤
#### 1. 调整``file``服务的配置
修改``server/configs/django/local_file.py``文件，取消以下代码的注释

```
# MINIO
STORAGE = {
    "CLIENT": os.environ.get("FILE_STORAGE_CLIENT", "MINIO"),  # 存储方式
    "OPTIONS": {
        "MINIO_ENTRYPOINT": os.environ.get("FILE_MINIO_ENTRYPOINT"),
        "MINIO_ACCESS_KEY": os.environ.get("FILE_MINIO_ACCESS_KEY"),
        "MINIO_SECRET_KEY": os.environ.get("FILE_MINIO_SECRET_KEY"),
    }
}
```

修改``server/scripts/config.sh``文件，填写MinIO的信息

```bash
export FILE_MINIO_ENTRYPOINT=<MinIO平台的地址>
export FILE_MINIO_ACCESS_KEY=<MinIO平台的登录账号>
export FILE_MINIO_SECRET_KEY=<MinIO平台的登录密码>
```

修改完配置后，如果服务已经正在运行，则执行以下命令重启服务

```Bash
$ cd server
$ ./scripts/deploy.sh start
```

#### 2. 修改nginx服务的配置文件
删除nginx已有的文件服务器配置文件``/etc/nginx/conf.d/tca_file_local.conf``文件，然后执行

```bash
rm /etc/nginx/conf.d/tca_file_local.conf
ln -s $CURRENT_PATH/configs/nginx/tca_file_minio.conf /etc/nginx/conf.d/tca_file_local.conf
```

> 也可以修改``server/scripts/init_config.sh``
>```Bash
> # 注释这一行
> ln -s $CURRENT_PATH/configs/nginx/tca_file_local.conf /etc/nginx/conf.d/tca_file_local.conf
> # 取消注释这一行
> ln -s $CURRENT_PATH/configs/nginx/tca_file_minio.conf /etc/nginx/conf.d/tca_file_local.conf
>```

修改完配置后，如果nginx已经正在运行，则执行``nginx -s reload``

### 结尾
以上两个步骤操作完成后，就可以通过``MinIO``存储文件了~