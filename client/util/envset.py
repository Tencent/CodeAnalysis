# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""配置task需要的环境变量
"""

import os
import re
import sys
import logging
import platform

from util.textutil import StringMgr

logger = logging.getLogger(__name__)


class EnvSet(object):
    """环境变量配置
    """
    def __update_os_environ(self, envs, task_mode = True):
        """
        添加到当前进程的环境变量中.将生效写进函数中，用于逐行生效，多条环境变量设置参数存在一定顺序的依赖。
        例如用户填写环境变量：
            JDK = /data/jdk1.9
            PATH = $JDK/bin:$PATH
        第二条参数需要在第一条已经生效的情况下执行，因此，环境变量设置改为逐条expandvars与update。
        由于函数功能改变，因此将名称改回update_os_environ。

        修改待设置的环境变量的编码，并更新到当前进程的环境变量列表中  -  将"当前系统"改为"当前进程"，将方法名"update_os_environ" 修改为"revise_os_environ_encode"
        增加该函数的原因是在Windows设置的环境变量值不能为unicode，
        如果为unicode且显式传递给subprocess模块，则会报错

        :param envs: dict - 待更新的环境变量列表

        """
        if not envs:
            return
        # 判断path环境变量的修改，是否包含path本身，若无则报出error信息
        if task_mode:
            for env_name, env_value in envs.items():
                if env_name.lower() == 'path':
                    # 检查PATH设置中是否有path本身的环境变量名
                    if env_value.lower().find('path') == -1:
                        logger.info('the path env error: %s' % env_value)
                        break
                    # 检查PATH设置中，PATH自身的引用是否正常，防止误写
                    if not env_value.lower().endswith('path'):
                        index = env_value.lower().find('path') + 4
                        if env_value[index] != ':' and env_value[index] != ';':
                            logger.info('the path env error: %s' % env_value)
                            break

        if platform.system() == 'Windows':
            for env_name, env_value in envs.items():
                new_envs = {}
                # windows设置环境变量，可能使用变量代替具体路径
                if re.match(r"^%.*%$", env_value.strip()):
                    env_value = os.environ.get(env_value.strip("%"), "")
                new_envs[env_name] = os.path.expandvars(env_value)
                os.environ.update(new_envs)
        else:
            for env_name, env_value in envs.items():
                logger.debug(f">>> set env {env_name}={os.path.expandvars(env_value)}")
                os.environ.update({env_name: os.path.expandvars(env_value)})

    def set_tool_env(self, tool_config):
        """设置工具环境变量, 将工具配置文件中的环境变量添加到当前进程环境变量中
        :param tool_config: 工具配置参数
            {
               "common":
                   {
                       "env_path"  : {"xxx": "xxx", "xxx": "xxx", ...},
                       "env_value" : {"xxx": "xxx", "xxx": "xxx", ...},
                       "path"      : ["xxx", "xxx"],
                       "tool_url"  : ["xxx", "xxx"]
                   },
                "tool_1": {...},
                "tool_2": {...},
                ...
            }
        :return: tool_envs,配置的环境变量
        """
        tool_envs = {}

        path_env = []
        for tool_name, tool_params in tool_config.items():
            # 添加路径类型的环境变量
            for env_name, full_path in tool_params["env_path"].items():
                if "PATH" == env_name:  # PATH应该单独放在path字段中，如果放在env_path中，忽略，避免影响和覆盖原有PATH变量
                    continue
                if env_name not in tool_envs:
                    tool_envs[env_name] = full_path

            # 添加值类型的环境变量
            for env_name, env_value in tool_params["env_value"].items():
                if env_name not in tool_envs:
                    tool_envs[env_name] = env_value

            # 将PATH的环境变量放到一个list中
            for rel_path in tool_params["path"]:
                if rel_path not in path_env:
                    path_env.append(rel_path)

        # 添加PATH环境变量
        path_str = os.getenv("PATH")    # 先读取系统PATH环境变量
        if path_str:
            path_list = path_str.split(os.pathsep)
        else:  # 增加判空，防止读取不到的情况
            path_list = []
        for full_path in path_env:
            # path不要去重,会影响加载顺序
            path_list = [full_path] + path_list  # 后添加的放在前面,优先搜索
        tool_envs["PATH"] = os.pathsep.join(path_list)

        # 调整环境变量编码
        self.__update_os_environ(tool_envs, False)

        return tool_envs

    def set_task_env(self, task_params):
        """
        设置任务环境变量,将 task params 中的环境变量配置添加到当前进程环境变量中
        :param task_params:
        :return:
        """
        if task_params:
            task_envs = task_params.get('envs', None)
            if task_envs:
                # 格式转换
                task_envs = StringMgr.str_to_dict(task_envs)
            else:
                task_envs = {}

            # 兼容之前的逻辑，根据参数设置 SUBMODULE_MODE 环境变量，供后续判断使用
            if "SUBMODULE_MODE" not in task_envs:
                ignore_submodule_clone = task_params.get("ignore_submodule_clone")
                ignore_submodule_issue = task_params.get("ignore_submodule_issue")
                if ignore_submodule_clone is False and ignore_submodule_issue is False:
                    if not ignore_submodule_clone:
                        task_envs["SUBMODULE_MODE"] = "True"

            if task_envs:
                # 设置到进程环境变量中
                self.__update_os_environ(task_envs, True)
                # logger.debug('设置任务环境变量::\n%s' % '\n'.join(['%s=%s' % (key, value) for key, value in task_envs.items()]))
        EnvSetting.env_setting_init()

    def get_origin_env(self, os_env=None):
        """
        由于pyinstaller打包后的二进制包执行时候，会修改依赖库搜索环境变量，如LD_LIBRARY_PATH
        所以在启动Subprocess执行命令时候，可能会影响到项目编译状况
        这里会返回启动二进制包之前的环境变量，提供给Subprocess使用
        1. linux和*BSD下会将LD_LIBRARY_PATH备份为LD_LIBRARY_PATH_ORIG，然后将二进制包生成的目录补充在LD_LIBRARY_PATH前面
        2. Aix下是LIBPATH和LIBPATH_ORIG
        3. Mac下是会unset掉DYLD_LIBRARY_PATH
        4. windows没有影响

        :param os_env: 系统环境变量dict,如果参数有传递,直接使用参数来操作,而不从os.environ里面取
        :return: env <dict>
        """
        if os_env:
            env = os_env
        else:
            env = dict(os.environ)

        # 判断是否是pyinstaller包状态, 若是源码状态，则不处理
        if len(sys.argv) > 0 and sys.argv[0].endswith(".py"):
            return env

        # Linux
        if sys.platform == "linux" or sys.platform == "linux2":
            lp_key = 'LD_LIBRARY_PATH'
            # 收集需要的lp环境变量
            wanted_env_list = []
            # 收集现有进程的lp环境变量，剔除掉pyinstaller添加的临时运行目录，则为需要传递给子进程的环境变量
            cur_lp_value = env.get(lp_key)
            if cur_lp_value:
                cur_lp_list = cur_lp_value.split(os.pathsep)
                for lp_value in cur_lp_list:
                    # 当前进程的lp环境变量，剔除掉pyinstaller添加的临时运行目录，其他的为需要的
                    if not lp_value.startswith("/tmp/_MEI"):
                        wanted_env_list.append(lp_value)
                if wanted_env_list:  # 现有的lp已经包含_ORIG
                    env[lp_key] = os.pathsep.join(wanted_env_list)
                    logger.debug(f"{lp_key}={cur_lp_value}, change to {env[lp_key]}")
                else:
                    env.pop(lp_key, None)
                    logger.debug(f"{lp_key}={cur_lp_value}, delete it.")

        # Mac:
        # 由于Mac下二进制包无法检测环境中环境变量原来是否有DYLD_LIBRARY_PATH，加上目前没有发现有项目遇到类似问题
        # 这里暂不做处理，继续观察

        return env


class EnvSetting(object):
    """
    通过类静态变量存储一些全局设置
    """
    # 全局设置 - 标注是否在拉代码时拉取子模块
    SUBMODULE_MODE = False

    @staticmethod
    def env_setting_init():
        '''
        初始化函数，于env生效后调用，通过os.env获取所有环境变量，通过遍历本类中的所有静态变量，载入对应数据
        计划支持数据类型：布尔型，整型，字符串
        支持设置名大小写兼容（统一小写后匹配）
        :return:
        '''
        env_keys = os.environ.keys()
        effective_list = []
        for attr_name in vars(EnvSetting).keys():
            if not attr_name.startswith('__') and attr_name != 'env_setting_init':
                if attr_name in env_keys:
                    # 将环境变量设置到EnvSetting类的静态变量中
                    setattr(EnvSetting, attr_name, os.environ[attr_name])
                    effective_list.append('%s - %s' % (attr_name, os.environ[attr_name]))
        logger.debug('设置生效清单： %s' % str(effective_list))
