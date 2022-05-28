# TCA Loong龙(测试版)
Java/Kotlin API和函数调用链分析工具

## 准备
- 部署TCA Server；
- 部署[CLS](../../server/cls/README.md#部署)，启动License校验功能；
- 在TCA Client的[config.ini](../../client/config.ini)中设置LICENSE_CONFIG信息。

## 使用
- 在TCA上创建对应的分析项目；
- 在分析项目对应的分析方案中添加JAAF/JAFC/JAFF工具的规则；
- 启动分析任务，等待任务执行完成，既可看到对应的问题。

## 自定义规则

### JAFC/JAFF
检查Java API:
- JAFC用于检测.java代码文件
- JAFF用于检测.class/.jar文件

规则参数格式如下：
- msg=用于上报时提示信息
- class=目标类名
- method=目标方法名称
- method_desc=目标api的参数和返回值类型，比如(Ljava/lang/String;Ljava/lang/Boolean;[Ljava/lang/Object;)Ljava/lang/Object;
- field=目标名称（不可与method同时填写）
- exclude=（可选）规则白名单，填写地址，多地址用分号隔开
- up_exist_method=（可选）填写函数2。目标被调用的函数调用链向上查找，若存在函数2，则报出。若未找到，则不报。
- up_no_exist_method=（可选）（与上相反）填写函数2。目标被调用的函数调用链向上查找，若不存在函数2，则报出。若存在，则不报。
- need_method_chain=（可选）true。表示获取目标函数的向上调用链数据（注意：该数据只会生成在本地task目录下，具体位置可以查看log）。

下面是参考示例：
```ini
class=org.apache.logging.log4j.Logger
method=error;warn;info;debug;fatal;trace;log
msg=扫描log4j api调用位置，辅助升级log4j
```

### JAAF
复杂场景下的Java API检查。支持检查继承自指定API A的代码中调用指定API B。

规则参数格式如下：
- msg=扫描结果上报时会展示的内容
- interface_class=被实现接口类名
- interface_method=被实现的函数名
- class=限制调用的API类名，书写方式同上类名
- method=限制调用的函数名，支持`;`分号相隔的批量查询

下面是参考示例：
```ini
msg=禁止在实现IQConfigProcessor-onParsed接口的代码中，调用如参数所述的handler-post等api。
interface_class=IQConfigProcessor
interface_method=onParsed
class=android.os.Handler
method=post;postAtTime;postDelayed;postAtFrontOfQueue
```
