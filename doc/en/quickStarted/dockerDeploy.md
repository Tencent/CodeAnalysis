# Docker rapid deployment（Recommended for a out of the box try）

:::warning
Docker deployment include Mariadb and Redis. Configuration file can be modified to indicate a MySQL/Mariadb and Redis, which satisfied operation and maintenance specification for extensive use.

:::

#### Requirements

- System
  - Linux, macOS or Windows
  - Minimum requirement：2-core processor, 4GB RAM, 100 GB available disk space
- Environment
  - Docker
- Privilege
  - Open port 80, 8000's access(80 for TCA's requests, 8000 for TCA Server)

#### To be deployed
Server, Web and Client

#### Operating instructions
##### First start

1. Enter the CodeAnalysis's work directory (e.g ``~/CodeAnalysis``), the following paths are relative paths within the directory.
2. Execute command:
    ```bash
    bash ./quick_install.sh docker deploy
    ```
::: tip
1. During docker deployment, the ``tencenttca/tca:latest`` image will be pulled from dockerhub by default.
2. During docker deployment, three paths will be mounted under the current root directory by default:
   - `.docker_temp/logs`：`/var/log/tca/` in container，TCA daily log output;
   - `.docker_temp/data`：`/var/opt/tca/` in container， TCA service data, mainly about Mariadb,Redis;
   - `.docker_temp/configs`：``/etc/tca`` in container，TCA configuration file，mainly `config.sh`
:::

##### Update
1. Update the code.
2. Execute command below:
```bash
TCA_IMAGE_BUILD=true ./quick_install.sh docker deploy  # Re-build and start TCA Container
```
::: tip
`TCA_IMAGE_BUILD=true` Indicates that the TCA image is built locally to run
:::



##### Run a Docker container
If `docker deploy` has been executed on the machine and the container data is retained, you can execute the following command to start the container and continue to run TCA

```bash
bash ./quick_install.sh docker start
```

##### Stop a Docker container
If a container is running and you want to stop it, you can run command

```bash
bash ./quick_install.sh docker stop
```

#### Use your TCA
Now, you have done the deployment of your first TCA. Please type `http://<Deploy server IP>` in your browser. click "立即体验", after login you can start your Tencent Code Analysis trip.  
More operation instructions please check：[Quick start a code analysis](../guide/快速入门/快速启动一次代码分析.md)
:::tip
Default account/Password：CodeDog/admin

If the default account password has been modified during deployment, please login according to the modified account and password.
:::
