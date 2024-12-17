# TCA

**欢迎体验 TCA Charts，期待您的反馈或PR~**

> 注意：
>
> - 请根据`Prerequisites`小节确认好版本好，使用默认的`values.yaml`即可部署
> - 可以根据业务情况调整`values.yaml`配置，比如默认的`passwordKey`、账号密码等敏感配置信息
> - TCA服务metrics方案正在完善，即将支持

## Introduction
This chart bootstraps a [TCA](https://github.com/Tencent/CodeAnalysis) deployment on a Kubernetes cluster using the [Helm](https://helm.sh/) package manager.

## **Prerequisites**
- Kubernetes 1.19+
- Helm 3.0.0+
- PV provisioner support in the underlying infrastructure

> Notice:
>
> - check Kubernetes version: `kubectl version`
> - check Helm version: `helm version`

## Installing the Chart
To install the chart with the release name `tca`:

```Bash
$ cd helm-charts
$ export RELEASE=tca
$ export NAMESPACE=tca
$ helm dependency update tca
$ helm install $RELEASE  --namespace $NAMESPACE --create-namespace tca/  --timeout 10m0s
```

The command deploys TCA on the Kubernetes cluster in the default configuration. The ``Parameters`` section lists the parameters that can be configured during installation.

## Uninstalling the Chart
To uninstall/delete the `tca` deployment:

```Bash
$ helm delete tca -n tca
```
The command removes all the Kubernetes components associated with the chart and deletes the release.

## Parameters
### Global parameters
| Name                                                    | Description                                             | Value          |
| ------------------------------------------------------- | ------------------------------------------------------- | -------------- |
| `global.imagePullPolicy`                                | Global Docker image registry                            | `""`           |
| `global.imagePullSecrets`                               | Global Docker registry secret names as an array         | `[]`           |

To create a secret to pull an image from a private container image registry or repository:
```Bash
$ kubectl create secret docker-registry ${SECRET_NAME} --docker-server=${DOCKER_SERVER} --docker-username=${DOCKER_USERNAME} --docker-password=${DOCKER_PASSWORD} --docker-email=${DOCKER_EMAIL}
```

### TCA Metric parameters
| Name                                                    | Description                                             | Value          |
| ------------------------------------------------------- | ------------------------------------------------------- | -------------- |
| `metrics.enable`                                        | provide endpoint to expose metrics                      | `false`        |


### TCA Ingress parameters

| Name                                                    | Description                                             | Value          |
| ------------------------------------------------------- | ------------------------------------------------------- | -------------- |
| `ingress.enable`                                        | Enable ingress record generation for TCA                | `true`         |
| `ingress.annotations`                                   | Additional annotations for the Ingress resource. To enable certificate autogeneration, place here your cert-manager annotations. | `{kubernetes.io/ingress.class: "nginx", nginx.ingress.kubernetes.io/proxy-body-size: "10240m"}`                     |


### TCA Nginx-ingress-controller parameters

Helm will deploy `nginx-ingress-controller` by default. Reference: [bitnami/nginx-ingress-controller](https://github.com/bitnami/charts/tree/main/bitnami/nginx-ingress-controller)

| Name                                                    | Description                                             | Value          |
| ------------------------------------------------------- | ------------------------------------------------------- | -------------- |
| `nginx-ingress-controller.enabled`                      | Enable nginx-ingress-controller for TCA                 | `true`         |
| `nginx-ingress-controller.defaultBackend.enabled`       | Enable nginx-ingress-controller default backend         | `true`         |


### TCA Internal Redis parameters
Helm will deploy `redis` by default. Reference: [bitnami/redis](https://github.com/bitnami/charts/tree/main/bitnami/redis)
> Notice: If you need to customize the Redis® configuration, you can supplement the variable configuration from above reference.

| Name                                   | Description                                                              | Value            |
| -------------------------------------- | ------------------------------------------------------------------------ | ---------------- |
| `redis.enable`                         | Deploy internal Redis® for TCA                                           | `true`           |
| `redis.auth.enabled`                   | Enable password authentication	                                        | `true`           |
| `redis.auth.password`                  | Redis® auth password                                                     | `tca2022`        |


### TCA External Redis parameters
> Notice: If using externalRedis, please disable deploying internal redis with helm: set `redis.enabled: false`.

| Name                                   | Description                                                              | Value            |
| -------------------------------------- | ------------------------------------------------------------------------ | ---------------- |
| `externalRedis.host`                   | External Redis® server host                                              | `""`             |
| `externalRedis.port`                   | External Redis® server port	                                            | `""`             |
| `externalRedis.password`               | External Redis® server auth password                                     | `""`             |


### TCA Internal Mariadb parameters
Helm will deploy `mariadb` by default. Reference: [bitnami/mariadb](https://github.com/bitnami/charts/tree/main/bitnami/mariadb)
> Notice: If you need to customize the Mariadb configuration, you can supplement the variable configuration from above reference.

| Name                                   | Description                                                              | Value            |
| -------------------------------------- | ------------------------------------------------------------------------ | ---------------- |
| `mariadb.enable`                       | Deploy internal Mariadb for TCA                                          | `true`           |
| `mariadb.auth.rootPassword`            | Password for the root user. Ignored if existing secret is provided.	    | `Tca@2022`       |
| `mariadb.auth.database`                | Name for a custom database to create	                                    | `codedog_main`   |
| `mariadb.primary.persistence.size`     | MariaDB primary persistent volume size	                                | `100Gi`          |
| `mariadb.initdbScriptsConfigMap`       | ConfigMap with the initdb scripts                                        | `tca-db-init`    |


### TCA External MySQL parameters
> Notice: If using externalMySQL, please disable deploying internal mariadb with helm: set `mariadb.enable: false`
> Notice: ExternalMySQL parameters will override internal mariadb parameters with helm.

| Name                                   | Description                                                              | Value            |
| -------------------------------------- | ------------------------------------------------------------------------ | ---------------- |
| `externalMySQL.host`                   | External Mysql server host                                               | `""`             |
| `externalMySQL.port`                   | External Mysql server port                                               | `""`             |
| `externalMySQL.username`               | External Mysql server username                                           | `""`             |
| `externalMySQL.password`               | External Mysql server password                                           | `""`             |

### TCA Common configuration parameters

| Name                                   | Description                                                              | Value                                                  |
| -------------------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------ |
| `tca.commonConfig.publicUrl`           | TCA web public url                                                       | `dev.tca.com`                                          |
| `tca.commonConfig.daemonFlag`          | TCA server debug mode                                                    | `False`                                                |
| `tca.commonConfig.accessLogPath`       | TCA server access log path, using "-" will print access log with STDOUT  | `-`                                                    |
| `tca.commonConfig.errorLogPath`        | TCA server error log path, using "-" will print access log with STDOUT   | `-`                                                    |
| `tca.commonConfig.apiTicketSalt`       | TCA server internal api ticket salt                                      | `a6x4c7esudcv396w`                                     |
| `tca.commonConfig.apiTicketToken`      | TCA server internal api ticket token                                     | `tca@public@2021`                                      |
| `tca.commonConfig.passwordKey`         | TCA server internal encryption key for sensitive data                    | `a6x4c7esudcv396w`                                     |
| `tca.commonConfig.nodeTicketSalt`      | TCA server internal encryption key for node connection                   | `a6x4c7esudcv396w`                                     |
| `tca.commonConfig.secretdKey`          | TCA server django secert key                                             | `25n=e*_e=4q!ert$4u#9v&^2n+)_#mi7&7ll@x29@j=w=k^q@^`   |
| `tca.commonConfig.defaultAdmin`        | TCA server default user username, use any 16 ascii characters.           | `CodeDog`                                              |
| `tca.commonConfig.defaultPassword`     | TCA server default user password, use any 16 ascii characters.           | `admin`                                                |
| `tca.commonConfig.defaultToken`        | TCA server default user token, use any 40 ascii characters.              | `0712b895f30c5e958ec71a7c22e1b1a2ad1d5c6b`             |                                         
| `tca.commonConfig.sentryDsn`           | TCA server sentry url config                                             | `""`                                                   |
| `tca.commonConfig.useLocalTool`        | Using local tools prepared in advance.                                   | `"false"`                                              |
| `tca.commonConfig.toolLoadUsername`    | Tencent Git Username for TCA client pulling analysis tools               | `""`                                                   |
| `tca.commonConfig.toolLoadPassword`    | Tencent Git Password for TCA client pulling analysis tools               | `""`                                                   |
| `tca.commonConfig.clsServerUrl`        | CLS server url                                                           | `""`                                                   |
| `tca.commonConfig.clsServerLicense`    | CLS server license                                                       | `""`                                                   |

>Notice: 
>- apiTicketSalt, passwordKey and nodeTicketSalt generation way: use any 16 or 32 ascii characters. The three values ​​can be kept the same.
>- api ticket token generation way: use any ascii characters.
>
> Generating a django key:
> ```Python
> # importing the function from utils
> from django.core.management.utils import get_random_secret_key
> # generating and printing the SECRET_KEY
> print(get_random_secret_key())
> ```
> Generating specify length key:
> ```Python
> import random, string
> length=16
> print(''.join(random.sample(string.ascii_lowercase + string.digits, length)))
> ```

### TCA Service configuration parameters
| Name                                 | Value                             |
| ------------------------------------ | --------------------------------- |
|`web`                                 | `tca.web.service`                 |
|`main`                                | `tca.main.server.service`         |
|`analysis`                            | `tca.analysis.server.service`     |
|`login`                               | `tca.login.server.service`        |
|`file`                                | `tca.file.server.service`         |
|`scmproxy`                            | `tca.scmproxy.server.service`     |
|`gateway`                             | `tca.gateway.server.service`      |

- Default TCA Service Configuraion

| Name                                 | Value                             |
| ------------------------------------ | --------------------------------- |
| `service.type`                       | `NodePort`                        |
| `service.ports.http`                 | `80`                              |
| `service.nodeport.http`              | `""`                              |

- TCA Web Service HTTPS configuration

| Name                                 | Value                             |
| ------------------------------------ | --------------------------------- |
| `tca.web.service.ports.https`        | `""`                              |
| `tca.web.service.nodeport.https`     | `""`                              |

- TCA Gateway Service HTTPS configuration

| Name                                 | Value                             |
| ------------------------------------ | --------------------------------- |
| `tca.gateway.service.ports.https`    | `""`                              |
| `tca.gateway.service.nodeport.https` | `""`                              |

### TCA Web configuration parameters

| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.web.image.repository`                   | TCA Web image repository                                                 | `tencenttca/tca-web`      |
| `tca.web.image.tag`                          | TCA Web image tag                                                        | `latest`                  |
| `tca.web.logPath`                            | TCA Web nginx log path                                                   | `/var/log/nginx`          |

### TCA Main configuration parameters
| Name                                         | Description                                                              | Value                 |
| -------------------------------------------- | ------------------------------------------------------------------------ |-----------------------|
| `tca.main.image.repository`                  | TCA Main image repository                                                | `tencenttca/tca-main` |
| `tca.main.image.tag`                         | TCA Main image tag                                                       | `latest`              |
| `tca.main.server.processnum`                 | TCA Main server process num                                              | `8`                   |
| `tca.main.worker.num`                        | TCA Main worker num for async starting analysis and handle periodic task | `2`                   |
| `tca.main.server.multiprocDir`               | TCA Main server storing monitoring indicator data path                   | `multiproc-tmp`       |

#### TCA Main setting configuration
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.main.settings.base.debugMode`           | TCA Main debug mode                                                      | `"true"`                  |
| `tca.main.settings.base.httpsCloneFlag`      | TCA Main dispatch scm url with https                                     | `"true"`                  |
| `tca.main.settings.dbName`                   | TCA Main database name                                                   | `"codedog_main"`          |
| `tca.main.settings.redisDBId`                | TCA Main redis database id                                               | `"1"`                     |
| `tca.main.settings.customDB.host`            | TCA Main custom mysql server host                                        | `""`                      |
| `tca.main.settings.customDB.port`            | TCA Main custom mysql server port                                        | `""`                      |
| `tca.main.settings.customDB.user`            | TCA Main custom mysql server user                                        | `""`                      |
| `tca.main.settings.customDB.password`        | TCA Main custom mysql server password                                    | `""`                      |
| `tca.main.settings.customRedis.host`         | TCA Main custom redis server host                                        | `""`                      |
| `tca.main.settings.customRedis.port`         | TCA Main custom redis server port                                        | `""`                      |
| `tca.main.settings.customRedis.password`     | TCA Main custom redis server password                                    | `""`                      |



### TCA Analysis Configuration parameters
| Name                                         | Description                                                   | Value                     |
|----------------------------------------------|---------------------------------------------------------------|---------------------------|
| `tca.analysis.image.repository`              | TCA Analysis image repository                                 | `tencenttca/tca-analysis` |
| `tca.analysis.image.tag`                     | TCA Analysis image tag                                        | `latest`                  |
| `tca.analysis.server.processnum`             | TCA Analysis server process num                               | `8`                       |
| `tca.analysis.worker.num`                    | TCA Analysis worker num for async saving lint and metric data | `2`                       |
| `tca.analysis.server.multiprocDir`           | TCA Analysis server storing monitoring indicator data path    | `multiproc-tmp`           |


#### TCA Analysis setting configuration
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.analysis.settings.base.debugMode`       | TCA Analysis debug mode                                                  | `"true"`                  |
| `tca.analysis.settings.dbName`               | TCA Analysis database name                                               | `"codedog_analysis"`      |
| `tca.analysis.settings.redisDBId`            | TCA Analysis redis database id                                           | `"0"`                     |
| `tca.analysis.settings.customDB.host`        | TCA Analysis custom mysql server host                                    | `""`                      |
| `tca.analysis.settings.customDB.port`        | TCA Analysis custom mysql server port                                    | `""`                      |
| `tca.analysis.settings.customDB.user`        | TCA Analysis custom mysql server user                                    | `""`                      |
| `tca.analysis.settings.customDB.password`    | TCA Analysis custom mysql server password                                | `""`                      |
| `tca.analysis.settings.customRedis.host`     | TCA Analysis custom redis server host                                    | `""`                      |
| `tca.analysis.settings.customRedis.port`     | TCA Analysis custom redis server port                                    | `""`                      |
| `tca.analysis.settings.customRedis.password` | TCA Analysis custom redis server password                                | `""`                      |


### TCA Login Configuration parameters
| Name                             | Description                                              | Value                    |
|----------------------------------|----------------------------------------------------------|--------------------------|
| `tca.login.image.repository`     | TCA Login image repository                               | `tencenttca/tca-login`   |
| `tca.login.image.tag`            | TCA Login image tag                                      | `latest`                 |
| `tca.login.server.processnum`    | TCA Login server process num                             | `8`                      |
| `tca.login.server.multiprocDir`  | TCA Login server storing monitoring indicator data path  | `multiproc-tmp`          |


#### TCA Login setting configuration
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.login.settings.base.debugMode`          | TCA Login debug mode                                                     | `"true"`                  |
| `tca.login.settings.dbName`                  | TCA Login database name                                                  | `"codedog_login"`         |
| `tca.login.settings.customDB.host`           | TCA Login custom mysql server host                                       | `""`                      |
| `tca.login.settings.customDB.port`           | TCA Login custom mysql server port                                       | `""`                      |
| `tca.login.settings.customDB.user`           | TCA Login custom mysql server user                                       | `""`                      |

### TCA File Configuration parameters
| Name                            | Description                                             | Value                 |
|---------------------------------|---------------------------------------------------------|-----------------------|
| `tca.file.image.repository`     | TCA file image repository                               | `tencenttca/tca-file` |
| `tca.file.image.tag`            | TCA file image tag                                      | `latest`              |
| `tca.file.server.multiprocDir`  | TCA file server storing monitoring indicator data path  | `multiproc-tmp`       |

#### TCA File setting configuration
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.file.settings.base.debugMode`           | TCA File debug mode                                                      | `"true"`                  |
| `tca.file.settings.dbName`                   | TCA File database name                                                   | `"codedog_file"`          |
| `tca.file.settings.customDB.host`            | TCA File custom mysql server host                                        | `""`                      |
| `tca.file.settings.customDB.port`            | TCA File custom mysql server port                                        | `""`                      |
| `tca.file.settings.customDB.user`            | TCA File custom mysql server user                                        | `""`                      |
| `tca.file.settings.storageClient`            | TCA File storage client mode, support modes: local/cos/minio             | `"local"`                 |
| `tca.file.settings.local.dirPath`            | TCA File saving files path                                               | `"/data/file"`            |
| `tca.file.settings.local.volumes.nfsServer`  | TCA File NFS server for saving files                                     | ``                        |
| `tca.file.settings.local.volumes.nfsPath`    | TCA File NFS server path for saving files                                | ``                        |
| `tca.file.settings.tencentcos.enabled`       | Enabled Tencent COS for TCA File saving files                            | `"false"`                 |
| `tca.file.settings.tencentcos.appId`         | Tencent COS appId value                                                  | `""`                      |
| `tca.file.settings.tencentcos.secretId`      | Tencent COS secretId value                                               | `""`                      |
| `tca.file.settings.tencentcos.secretKey`     | Tencent COS secretKey value                                              | `""`                      |
| `tca.file.settings.tencentcos.region`        | Tencent COS region value                                                 | `""`                      |
| `tca.file.settings.tencentcos.rootBucket`    | Tencent COS root Bucket name value                                       | `""`                      |
| `tca.file.settings.minio.enabled`            | Enabled MinIO for TCA File saving files                                  | `"false"`                 |
| `tca.file.settings.minio.entrypoint`         | MinIO server url                                                         | `""`                      |
| `tca.file.settings.minio.accessKey`          | MinIO server access key                                                  | `""`                      |
| `tca.file.settings.minio.secretKey`          | MinIO server secret key                                                  | `""`                      |


### TCA Scmproxy Configuration parameters
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.scmproxy.image.repository`              | TCA scmproxy image repository                                            | `tencenttca/tca-scmproxy` |
| `tca.scmproxy.image.tag`                     | TCA scmproxy image tag                                                   | `latest`                  |
| `tca.scmproxy.privateScmUrl`                 | TCA scmproxy private scm url                                             | `""`                      |

### TCA Client Configuration parameters
#### Default node pool configuration
| Name                                           | Description                                  | Value                    |
|------------------------------------------------|----------------------------------------------| ------------------------ |
| `tca.client.image.repository`                  | TCA client image repository                  | `tencenttca/tca-client`  |
| `tca.client.image.tag`                         | TCA client image tag                         | `latest`                 |
| `tca.client.enabeld`                           | Enabled starting TCA client with helm        | `true`                   |
| `tca.client.replicas`                          | The number of nodes in the default node pool | `1`                    |
| `tca.client.tag`                               | Tag of the extra node pool                   | `Codedog_Linux`         |
| `tca.client.resources.limits.cpu`              | The upper limit of cpu usage                 | `2000m`                 |
| `tca.client.resources.limits.memory`           | The upper limit of memory usage              | `4Gi`                   |
| `tca.client.resources.requests.cpu`            | Required cpu resources                       | `1000m`                 |
| `tca.client.resources.requests.memory`         | Required memory resources                    | `2Gi`                   |

#### Client Node pool expansion operations guide
You can configure node resources on the client. 
If you do not manually configure node resources, the default node pool is used.
If the node pool resources are insufficient, expand the capacity of the node pool at any time. For details, refer to 'Procedure for expanding a node pool'.

#### TCA client node pool expansion config
| Name                                                         | Description                                    |
|--------------------------------------------------------------|---------------------------------------|
| `extraNodePools.nodepool`                                      | Name of the extended node pool        |
| `extraNodePools.nodepool.tag`                                  | Tag of the extra node pool            |
| `extraNodePools.nodepool.enabled`                              | Enabled extending node pool with helm |
| `extraNodePools.nodepool.replicas`                             | The number of nodes in the extra node pool                              |
| `extraNodePools.nodepool.resources.limits.cpu`                 | The upper limit of cpu usage                           |
| `extraNodePools.nodepool.resources.limits.memory`              | The upper limit of memory usage                            |
| `extraNodePools.nodepool.resources.requests.cpu`               | Required cpu resources                              |
| `extraNodePools.nodepool.resources.requests.memory`            | Required memory resources                               |

#### Procedure for expanding a node pool
1. Initially, deploy the project exclusively utilizing the default node pool.
2. To expand the node pool, navigate to "Background Management > Node Management > Label Management" and add label information.
3. Update the extra node pool configuration in the project file by navigating to "CodeAnalysis/helm-charts/tca/values.yaml" .
4. To add configuration information for extra node pools, refer to the "TCA client node pool expansion config" section under "extraNodePools" in the client section of the TCA.
5. Please note that the "extraNodePools.nodepool" tag can be customized to match the user's requirements for the node pool name. This tag should be the same as the tag name added in Step 2.
6. To enable the current node pool, modify the "enabled" value to "true".
7. Update project deployment.

### TCA Gateway Configuration parameters
| Name                                         | Description                                                              | Value                     |
| -------------------------------------------- | ------------------------------------------------------------------------ | ------------------------- |
| `tca.gateway.image.repository`               | TCA gateway image repository                                             | `nginx`                   |
| `tca.gateway.image.repository`               | TCA gateway image tag                                                    | `1.13.7`                  |
