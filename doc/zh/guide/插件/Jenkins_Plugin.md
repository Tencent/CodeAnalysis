# Jenkins插件使用说明
::: tip
以下说明以 Jenkins 2.361.2 版本为例。
:::

## 使用前准备
### 编译打包Jenkins插件
在 TCA 源码的`plugin/jenkins_plugin`目录下，执行命令`mvm package -DskipTests`，打包完成后进入target目录会看到Jenkins_plugin.hpi 的安装包


### 在Jenkins安装插件
在Jenkins中通过【Manage Plugin】-> 【Advanced】->【Deploy plugin】的方式选择 Jenkins_plugin.hpi文件上传安装，并重启Jenkins。  
![](../../../images/jenkins_manage_plugins.png)
<img src="../../../images/jenkins_deploy_plugin.png" width = "500"/>

最终在【Installed】里搜索出【TCA】代表插件安装成功。
![](../../../images/jenkins_installed_plugins.png)


## 使用插件
### 在 TCA 创建团队和项目
如已创建后待使用的团队和项目，可跳过此步。

进入已部署好的TCA页面，点击【创建团队】，成功后【创建项目】。

### 配置Jenkins环境变量
进入Jenkins设置界面，在【Manage Jenkins】->【Configure System】->【Global properties】中添加环境变量：  
Name：`PYTHONPATH`      Value：xxxx（路径不包含python3）  
Value：`GITPATH`        Value：xxxx（路径不包含git）  
![](../../../images/jenkins_var_path.png)
![](../../../images/jenkins_manage_jenkins.png)
<img src="../../../images/jenkins_environment_vars.png" width = "400"/>


### 创建一个构建任务，配置代码库信息
进入Jenkins，通过【New Item】创建一个空白任务，在任务配置中【Source Code Management】配置待分析的代码库地址和凭证。  
`Repository URL`: 填入远端仓库地址  
`Credentials`: 添加仓库的用户名和密码作为凭证，如果是公开仓库，可以不设置仓库凭证

<img src="../../../images/jenkins_new_item.png" width = "300"/>

![](../../../images/jenkins_git_config.png)

### 配置 TCA 插件
在构建任务的【Build】中选择【TCA】插件并配置以下参数： 

`CodeAnalysis`: 拉取代码所在的绝对路径  
`团队ID`: 在 TCA 中创建的团队的标识ID，可在TCA【团队概览】中获取“团队唯一标识”  
`项目名称`: 在 TCA 中创建的项目的标识ID，可在TCA【项目概览】中获取“项目唯一标识”  
`Token`: 在 TCA 的【个人中心】->【个人令牌】中获取  
`分支名称`: 需要扫描的代码分析名称  
`语言类别`: 项目需要扫描的语言  
`分析方案模板ID`: 需要使用的分析方案模板ID，在分析方案模板的“基础属性”中获取，将根据此模板创建分析方案（选填）  
`分析方案名称`: 指定创建出来的分析方案的名称（选填）  
`全量扫描`: 不勾选默认启动增量扫描   
`质量门禁`: 设置质量门禁值，配置和使用参考 [设置质量门禁](#设置质量门禁)

配置完成后点击【Save】保存。

![](../../../images/jenkins_tca_plugin_config.png)

### 启动构建并查看结果
点击【Build Now】启动构建。  
进入构建任务，在【Console Output】中查看执行过程。  
执行完成后，可在下方看到代码分析的结果链接，也可在【代码分析报告】中获取代码分析的json报告。  
![](../../../images/jenkins_build.png)
<img src="../../../images/jenkins_console_output.png" width = "300"/>
![](../../../images/jenkins_output_url.png)

## 设置质量门禁
在上述 TCA 插件配置部分填写`质量门禁`参数，需要填写一个整数，即当前分支的扫描问题量大于该质量门禁值时，判断为不通过；否则为通过。完成后会将TCA结果状态（`success`|`failure`）输出到工作空间下的`tca_threshold.txt`文件中，供后续步骤判断和终止流水线。

在TCA插件后增加shell命令步骤，输入以下脚本内容：

![](../../../images/jenkins_shell.png)

```shell
tca_status=`cat tca_threshold.txt`
if [ "${tca_status}" == "success" ]; then
  echo ">> tca scan pass!"
else
  echo ">> tca scan fail! exit code 255"
  exit 255
fi
```

当质量门禁不通过时，会终止流水线（退出码：255）。
