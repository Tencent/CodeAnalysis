# Eslint 使用手册

代码分析支持 Eslint 分析，并支持用户自由扩展配置。

## 适用场景

目前 TCA-Eslint 的适用场景很广，灵活扩展：

- JavaScript
- TypeScript
- React
- Vue
- Google 代码规范分析
- 其他，包括项目自己维护的 Eslint 配置

## 快速接入

以下是接入步骤：

1. 在代码分析创建项目，会自动匹配 JavaScript 或者 TypeScript 对应的推荐规则集
2. 启动分析即可

## 高级配置

### 基础概念

在进行高级配置之前，这里先普及下代码分析这边的基础概念——Eslint 类型。
由于 JavaScript 语法、 Vue 语法和 TypeScript 语法之间的区别，三者使用的语法解析器也是不一样的，这里基于其使用的语法解析器的不同，从 Eslint 中拆分出来了 Eslint_vue 和 Eslint_typescript 工具。可以根据需要选择对应工具下的规则进行分析。而配置也会基于类型的不同匹配到对应的工具中。
目前代码分析上 Eslint 类型有：

- JAVASCRIPT
  分析 JavaScript 以及基于 JavaScript 写的 React 代码，默认分析文件后缀名为.js,.jsx
- VUE
  分析 Vue 框架的代码，默认分析文件后缀名为.vue
- TYPESCRIPT
  分析 TypeScript 以及基于 TypeScript 写的 React 代码，默认分析文件后缀名为.ts,tsx

### 设置 Globals

因为项目会用到各式各样的框架，其中会有全局变量是 Eslint 无法识别到的，比如 `_` 或者 jtest，从而导致分析出不少误报。这里支持使用下面环境变量设置这些全局变量，减少误报。可以在代码分析项目中设置对应的环境变量。

| 环境变量名称              | 描述               |
| :------------------------ | :----------------- |
| ESLINT_JAVASCRIPT_GLOBALS | 字符串，以分号分割 |
| ESLINT_VUE_GLOBALS        | 字符串，以分号分割 |
| ESLINT_TYPESCRIPT_GLOBALS | 字符串，以分号分割 |

比如：

```shell
ESLINT_JAVASCRIPT_GLOBALS=_:readonly;jtest:readonly
```

其中，

- writable 表示允许重写变量
- readonly 表示不允许重写变量
- off 表示禁用该全局变量

### 指定参数配置文件

代码分析执行 Eslint 分析，默认会使用 Alloy Team 的 Eslint 配置来分析，但是也支持修改配置。

1. 在代码库中创建一个参数配置 Json 文件，结果类似 Eslint 的 Json 配置文件
2. 在代码分析项目设置下面对应环境变量，指向这个参数配置文件
   指定了参数配置文件之后，Eslint 分析时候就会自动将代码分析默认的配置与该参数配置文件进行合并。
3. 启动全量分析即可

| 环境变量名称              | 描述                         |
| :------------------------ | :--------------------------- |
| ESLINT_JAVASCRIPT_OPTIONS | 字符串，相对代码库根目录路径 |
| ESLINT_VUE_OPTIONS        | 字符串，相对代码库根目录路径 |
| ESLINT_TYPESCRIPT_OPTIONS | 字符串，相对代码库根目录路径 |

### 指定 Eslint 配置文件

代码分析也支持用户指定自己维护的 Eslint 配置文件进行分析。

| 环境变量名称             | 描述                         |
| :----------------------- | :--------------------------- |
| ESLINT_JAVASCRIPT_CONFIG | 字符串，相对代码库根目录路径 |
| ESLINT_VUE_CONFIG        | 字符串，相对代码库根目录路径 |
| ESLINT_TYPESCRIPT_CONFIG | 字符串，相对代码库根目录路径 |

### 设置配置类型

代码分析自带支持 Google 代码规范，可以在代码分析项目设置对应环境变量，使用对应的配置文件。

| 环境变量名称                  | 描述                                            |
| :---------------------------- | :---------------------------------------------- |
| ESLINT_JAVASCRIPT_CONFIG_TYPE | 字符串, google,default,custom                 |
| ESLINT_VUE_CONFIG_TYPE        | 字符串, 可选：default,custom                    |
| ESLINT_TYPESCRIPT_CONFIG_TYPE | 字符串, 可选：default,custom                    |

其中：

- google，表示使用 google 代码规范配置文件
- default，表示使用代码分析维护的配置文件
- custom，表示使用项目代码库中 Eslint 配置文件

### 配置优先顺序

这里介绍 TCA-Eslint 的配置使用顺序：

1. 优先检查是否设置对应的 ESLINT_CONFIG 环境变量，比如 ESLINT_JAVASCRIPT_CONFIG
2. 然后检查是否设置对应的 ESLINT_CONFIG_TYPE 环境变量，比如 ESLINT_JAVASCRIPT_CONFIG_TYPE
3. 若是 JAVASCRIPT 类型的项目，会自动检测代码库根目录下是否有 ESLINT 配置文件，若有则使用该配置文件进行分析，其他类型的项目便不会有这一步
4. 使用代码分析维护的 Alloy Team 的配置文件进行分析

### 分析路径配置

可以在代码分析页面上设置分析路径设置，这里建议多使用 Exclude 设置，因为 Eslint 工具本身对 include 支持不友好。

## Q&A

Q：JavaScript 内存溢出

A：Eslint 执行可能会出现 Js 内存溢出，以下有三种方案可以解决：

- 可以设置环境变量 NODE_OPTIONS，比如

```shell
NODE_OPTIONS="--max-old-space-size=4096"
```

- 设置环境变量 ESLINT_MAX_OLD_SPACE_SIZE，比如

```shell
ESLINT_MAX_OLD_SPACE_SIZE=4096
```

- 设置分析路径过滤，将无用的文件进行过滤

Q：一个配置同时分析 JS 和 TS

A：若代码库中既有 JavaScript 代码，又有 TypeScript 代码，并且共用一个配置文件。
若规则集中既有 Eslint 规则又有 Eslint_typescript 规则，为了避免执行两次 Eslint 以及可能出现重复单的情况，并且因为 Eslint_typescript 的语法解析器也能够解析 JavaScript 代码，所以这里将这样的项目当作 TypeScript 项目。

1. 这里建议只指定 ESLINT_TYPESCRIPT_CONFIG 环境变量
2. 规则集中剔除 Eslint 的规则，只保留 Eslint_typescript 规则。
3. 并指定 ESLINT_TYPESCRIPT_EXT=.js,.jsx,.ts,.tsx

Q：找不到依赖

A：用户自己配置的配置文件中，可能会用到代码分析没有管理到的规则插件，导致分析时候找不到对应的依赖，这里有两个方案提供解决：

- 在代码库根目录下 npm 安装对应插件，并设置分析路径过滤 node_modules

Q：custom 与指定配置文件的区别

A：- custom 模式，会检测代码库中的 Eslint 配置文件进行分析，包括子目录和代码注释中设置的配置，都是可以生效的。

- 相对的，指定配置文件的方式，只会对指定的配置文件中的配置会生效。
