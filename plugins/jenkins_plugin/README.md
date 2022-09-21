
# 版本要求
Jenkins 2.277.1及以上  

# 如何使用插件
https://github.com/Tencent/CodeAnalysis/blob/main/plugins/jenkins_plugin/TCA_Jenkins_Plugin.pdf 

# 设置质量门禁

1. 在TCA插件配置`质量门禁`参数，填写一个整数，当前分支的扫描问题量大于质量门禁值时，判断为不通过；否则为通过。完成后会将TCA结果状态（`success`|`failure`）输出到工作空间下的`tca_threshold.txt`文件中，供后续步骤判断和终止流水线。
2. 在TCA插件后增加shell命令步骤，输入以下脚本内容：

```commandline
tca_status=`cat tca_threshold.txt`
if [ "${tca_status}" == "success" ]; then
  echo ">> tca scan pass!"
else
  echo ">> tca scan fail! exit code 255"
  exit 255
fi
```

当质量门禁不通过时，会终止流水线（退出码：255）。