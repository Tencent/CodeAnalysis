# Enhanced Analysis Module Deployment

In addition to integrating well-known analysis tools in the industry, TCA also has its own independently developed tools, which serve as the enhanced analysis module of TCA.

The TCA enhanced analysis module requires users to additionally deploy the License authentication microservice and apply for a License by email.

::: tip
**1. License application is completely free!**
2. Enterprises or universities are given priority in applying for a License.
:::

## Concepts
- Independent tools: Code analysis tools independently developed by TCA;
- CLS(Common License Server): The License authentication microservice for TCA independent tools.

## Module Features
- Supports Objective-C/C++ code specification check;
- Supports analysis of project dependency components;
- Supports analysis of whether dependency components have vulnerabilities and other issues;
- Supports Java/Kotlin API and function call chain analysis;
- Supports code safety, null pointer check, memory leak, and other rules.

**Continuously updating...**

## TCA official website version enhanced capability application
If users usually use [TCA official website version public service](https://tca.tencent.com/) and want to experience the analysis capabilities of the enhanced analysis module on the official website version, they can follow [this help document](https://tca.tencent.com/document/zh/guide/%E5%AE%A2%E6%88%B7%E7%AB%AF%E6%8E%A5%E5%85%A5/License%E9%85%8D%E7%BD%AE.html) to apply for configuration.

## TCA Private Deployment Enhanced Capability Application
If you are using TCA in an enterprise intranet environment and want to experience the enhanced analysis module capabilities of TCA on the intranet, you can apply as follows.

### Preparation
- A dedicated machine for the CLS microservice, the CLS microservice needs to be bound to this machine

::: warning
**Note: The CLS directory cannot be deleted at will**
:::

### Steps
1. Execute the following command in the `server/cls` directory of the TCA source code to obtain the `Server ID` and `Client License`

::: warning
**Note: The command needs to be executed in the CLS directory**
:::

```shell
# install Git LFS
$ bash ./scripts/base/install_git_lfs.sh
# If the cls binary is not found in this directory, you can execute the following command to synchronize.
$ bash ./scripts/base/install_bin.sh
$ cd server/cls
$ ./cls server
2022-04-13 18:35:29.356510559 +0800 CST [INFO] Version: 20220328.1
2022-04-13 18:35:29.44083463 +0800 CST [INFO] The client license is:
xxx
2022-04-13 18:35:29.454552966 +0800 CST [INFO] License Server ID: xxx
```
- `Server ID`: Machine code, used to apply for License authorization from the TCA team
- `Client License`: Provided to the TCA Client to facilitate tool authentication (important, it is recommended to back up)

2. Configure the CLS microservice information in the `config.ini` of the TCA Client directory, for example

```ini
[LICENSE_CONFIG]
; [optional] Fill in when using independent tools, no need by default
; Domain name and port of the License service
URL=http://<IP or domain name>:<port>
BASE_PATH=
LICENSE=<Client License>
```

::: warning
Note: The URL corresponding value does not need to follow the slash `/` at the end.
:::

::: warning
Different deployment methods can modify the `config.ini` configuration according to the following methods:

- Source code deployment:
  - Modify the `client/config.ini` in the source code directory
  - Restart the client: `./quick_install.sh local start client`
- Docker deployment:
  - Method 1: Modify the `.docker_temp/configs/client/config.ini` in the source code directory and restart the `tca-services` container
  - Method 2: Enter the `tca-service` container, modify `/CodeAnalysis/client/config.ini`, and exit and restart the `tca-services` container
  - Restart the container method: `docker restart tca-service`
- Docker-Compose deployment:
  - Modify the `client/config.ini` in the source code directory and restart the `client` container
  - Restart the container method: `docker-compose restart client`
:::

3. Submit a private cloud license application on the TCA Cloud official website
- (1) Register or log in to an account on the [TCA Cloud official website](https://tca.tencent.com/);
- (2) Enter the team that needs to apply for a private cloud license (if there is no team, you need to create a corresponding team);
- (3) On the team page, enter the [Node Management]->[Private Cloud License Configuration] page in turn, then click the [Apply for License] button in the upper right corner, fill in the relevant information and submit the application. The specific information is as follows:
  - Applicant name
  - Applicant's organization name
  - Applicant's organization type: company/university/individual
  - Applicant's email address
  - Applicant's mobile phone number
  - Server ID: `Server ID` output in step 1, the machine code for the first registration
  - Client License: `Client License` output in step 1
  - Application scenario
- (4) Then wait for the application license to be reviewed and approved, you can copy the private cloud license and continue with the following step 4.

4. Fill in the License in the `config.yaml` file in the CLS directory  

::: warning
Note: Follow the yaml format, for example:
- In key-value pairs, there is a blank character after the colon `:`, for example `key: value`.
:::

5. Execute the following command to start CLS

```shell
./cls server -d
```

6. Verify that the CLS process starts normally

```bash
# Find if there is a CLS process
ps aux|grep cls
```

::: warning
Note: If the above command does not find the CLS process, it means that CLS did not start normally.  
Please try to change the port in the `config.yaml` file to another port, such as 8080, the default is port 80, and then re-execute the command in step 5.
:::

7. Start the TCA analysis task
Check the independent tool-related rule package in the analysis plan on the TCA platform, such as the dependency component analysis rule package, and then start an analysis task. If it runs normally, it means the setting takes effect.

### CLS Operation and Maintenance
#### Automatic Restart
```shell
# Find the CLS process ID
ps aux|grep cls
# Restart the microservice
kill -USR2 <pid>
```

#### Network Exception
If the above deployment steps have been completed, but the enhanced function still encounters the `License check failed! Please check the license. License Server is not available!` exception. You can troubleshoot as follows:

- Enter the task page, click on the abnormal tool, and download the execution log of the tool. If the following logs appear in the log, it means that the network access to CLS is abnormal;
```log
method(head) call fails on error: <urlopen error [Errno 111] Connection refused>
```
- Continue to verify. If it is Docker or Docker-Compose deployment method, enter the TCA Client container. If it is a source code deployment, go to the TCA Client machine. Execute the following command to confirm whether the network is accessible:
```bash
ping <CLS IP or domain name filled in config.ini>
telnet <CLS IP or domain name filled in config.ini> <corresponding port>
```
- If the network is not accessible, please check:
  * Whether the firewall has opened the corresponding port;
  * Whether the corresponding domain name of CLS is set in the host;
  * Whether the IP setting is wrong.

##### Case Sharing
Background:
Xiao Ming deployed TCA in Docker mode and deployed the CLS service on the same host. Then he set the IP in the URL in config.ini to `127.0.0.1`, restarted and started the enhanced function task and encountered the above network disconnection exception.  
Reason:
The reason is that the `127.0.0.1` at this time points to the TCA Client container itself, not the CLS service deployed on the host.  
Solution:
Change `127.0.0.1` to the host's own IP.

#### CLS Update

1. Use the following command to find the cls process and kill the process
```shell
# Find the CLS process ID
ps aux|grep cls
# Restart the microservice
kill -9 <pid>
```
2. Download the latest version of cls and replace the cls binary file in it  
::: warning
Note: You cannot delete the original cls directory, you only need to replace the cls binary file in it.
:::
3. Use the following command to restart the cls service
```shell
./cls server -d
```
