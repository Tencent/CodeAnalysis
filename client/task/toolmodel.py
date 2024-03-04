# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

'''
工具模板类，用于直接封装工具
'''

from task.basic.datahandler.formater import NORMAL_FORMAT
from task.basic.datahandler.blamer import NORMAL_BLAME
from task.basic.datahandler.filter import DIFF_FILTER, REVISION_FILTER, PATH_FILTER
from task.basic.datahandler.submodulehandle import NORMAL_SUBMODULE_HANDLE
from task.basic.datahandler.packdiffinfo import NORMAL_DIFFINFO
from task.basic.datahandler.issuehash import NORMAL_ISSUE_HASH
from task.basic.datahandler.issuesplit import NORMAL_ISSUE_SPLIT
from task.basic.datahandler.addfileinfo import NORMAL_ADD_FILE_INFO
from task.basic.datahandler.addpersoninfo import NO_ADD_PERSON_INFO
from util.tooldisplay import ToolDisplay


class IToolModel(object):
    # 默认值，可以在具体工具逻辑中修改;默认版本的工具,扫描结果已经拆解,不保存在response.json中
    version = "3.0"

    def __init__(self, params):
        self.middle_data = {}  # 工具通过middle_data进行每个步骤的结果传输
        self.sensitive = ToolDisplay.is_sensitive_tool(params)  # 通过参数判断工具是否敏感
        self.sensitive_word_maps = {}
        pass

    def print_log(self, message):
        """
        将日志中的敏感词替换掉，再打印日志
        :param message:
        :return:
        """
        ToolDisplay.print_log(self.sensitive, self.sensitive_word_maps, message)

    def compile(self, params):
        '''
        编译执行函数
        :param params: 编译所需要的资源 1.项目地址 2. 编译命令 3. 环境变量参数 4.编译结果生成地址
        :return:
        '''
        raise NotImplementedError()

    def analyze(self, params):
        '''
        分析执行函数
        :param params: 分析所需要的资源 1.项目地址 2.工作地址 3.分析参数
        :return:
        '''
        raise NotImplementedError()

    def set_format_type(self):
        '''
        通过覆盖该函数来选择format类型
        目前存在format类型有：
        1. NORMAL_FORMAT 常规format
        2. DUPLICATE_FORMAT 重复代码扫描的结果格式化
        由于format类型互斥，所以既能返回一个值
        :return:
        '''
        return NORMAL_FORMAT

    def set_blame_type(self):
        '''
        通过覆盖该函数来选择blame类型
        目前存在blame类型有：
        1. NO_BLAME 不需要blame
        2. NORMAL_BLAME 常规blame
        3. FILE_LAST_CHANGE_BLAME 将文件最后一个修改人作为责任人
        4. DUPLICATE_BLAME 获取重复代码块的最近修改信息
        5. CCN_BLAME 获取圈复杂度的最近修改信息
        由于blame类型互斥，所以既能返回一个值
        :return:
        '''
        return NORMAL_BLAME

    def set_filter_type_list(self):
        '''
        通过覆盖该函数来选择过滤类型
        目前存在的过滤类型有：
        1. NO_FILTER  不需要过滤
        2. DIFF_FILTER 将非修改的代码文件进行过滤
        3. REVISION_FILTER 通过起始版本号进行过滤
        4. PATH_FILTER 通过用户设置的黑白名单进行过滤
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        '''
        return [DIFF_FILTER, REVISION_FILTER, PATH_FILTER]

    def set_submodule_handle(self):
        """
        通过覆盖该函数来选择子模块处理类型
        目前存在的过滤类型有：
        1. NO_SUBMODULE_HANDLE  不需要子模块处理
        2. NORMAL_SUBMODULE_HANDLE 当SUBMODULE_MODE为on时候，获取子模块文件信息
        3. CCN_SUBMODULE_HANDLE 当SUBMODULE_MODE为on时候，对CCN结果获取子模块文件信息
        过滤选项可以多选，但NO_FILTER为阻止使用过滤器
        :return:
        """
        return NORMAL_SUBMODULE_HANDLE

    def set_inc_source_path_list(self):
        '''
        用于设置该工具使用增量资源的缓存目录
        默认只增量缓存'source_dir'
        部分工具会需要缓存'source_dir','work_dir'
        :return: 需要缓存的目录名
        '''
        return ['source_dir']  # 考虑试用setting里面的字段

    def set_inc_source_type(self):
        '''
        用于设置增量资源的类型，当不同工具需要使用同一个增量资源时直接默认使用Normal
        例如androidlint与findbugs可以复用
        部分工具会需要单独使用一个增量资源，因此单独创建一个类型出来
        :return: 增量资源类型，一般直接使用工具名即可
        '''
        return 'normal'

    def set_result_pack_diff_info(self):
        '''
        用于设置扫描结果是否需要加入项目代码文件的diff信息
        默认工具需要上报diff信息，目前已知代码统计不需要
        :return: 是否需要上传
        '''
        return NORMAL_DIFFINFO

    def set_issue_hash(self):
        '''
        用于设置issue hash值计算
        :return: 是否需要上传
        '''
        return NORMAL_ISSUE_HASH

    def set_issue_split(self):
        '''
        用于设置是否将扫描结果拆分成多个issue json文件,以防止json文件过大server无法加载的情况
        默认工具需要拆分
        :return: 是否需要拆分
        '''
        return NORMAL_ISSUE_SPLIT

    def set_issue_ignore_type(self):
        '''
        设置问题忽略的类型
        :return:
        '''
        raise NotImplementedError

    def set_mid_source_path_list(self):
        '''
        区别于增量资源的管理，编译与分析task之间的数据传递也需要控制
        例如：编译后传递的是idir中的中间文件，但不排除某些工具需要编译过后的项目代码文件
        因此这里暂时默认将workdir作为需要传递的中间文件
        :return:
        '''
        return ['work_dir']

    def set_add_file_info(self):
        """
        设置增加文件层级信息
        :param params:
        :return:
        """
        return NORMAL_ADD_FILE_INFO

    def set_tool_skip_condition(self, params):
        '''
        用于实现判断条件，跳过本次工具扫描。
        适用场景：例如当工具扫描前，判断项目变更内容中无代码文件
        :return:
        '''
        return False

    def set_no_branch_diff_skip(self, params):
        '''
        与对比分支无差异时，是否跳过。
        适用场景：codelint类型工具跳过；codemetric类型工具不跳过。
        :return:
        '''
        return False

    def set_add_person_info(self):
        """
        增加person维度的概览数据
        :return:
        """
        return NO_ADD_PERSON_INFO

    def check_tool_usable(self, tool_params):
        '''
        检查工具是否可以用，具体检查内容：
        注意：此部分只检查compile与analyze等工具所属的步骤，datahandle不属于此部分
        :return:支持该工具的task类型数组，若不支持返回空数组
        '''
        default_tool_usable_set = []
        try:
            self.compile(None)
        except NotImplementedError:
            pass
        except:
            default_tool_usable_set.append('compile')
        try:
            self.analyze(None)
        except NotImplementedError:
            pass
        except:
            default_tool_usable_set.append('analyze')
        return default_tool_usable_set

    def get_private_processes(self):
        '''
        # 需求内容
        每个工具可以设置一个private_processes list，设置需要返回给原来机器跑的进程
        可以默认都是["datahandle"]
        :return:
        '''
        return ['datahandle']
