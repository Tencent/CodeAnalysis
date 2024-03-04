# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""节点模块核心逻辑
"""
# 2021-03-29    jerolin    created

# 原生 import
import logging

# 第三方 import
from django.utils.timezone import now

# 项目内 import
from apps.authen.core import OrganizationManager
from apps.job.models import Task, TaskProcessRelation
from apps.nodemgr import models
from apps.scan_conf import models as scan_conf_models

logger = logging.getLogger(__name__)


class NodeManager(object):
    """节点管理
    """

    @classmethod
    def get_node_ip(cls, request):
        """通过request请求获取节点IP
        """
        try:
            if request.data.get("puppy_ip"):
                node_ip = request.data["puppy_ip"]
            else:
                ips = request.META["HTTP_X_FORWARDED_FOR"]
                node_ip = ips.split(',')[0].strip()
            return node_ip
        except Exception as err:
            logger.warning("Get node ip failed: %s" % err)
            ip = request.META.get('HTTP_X_REAL_IP') or request.META['REMOTE_ADDR']
            return ip

    @classmethod
    def refresh_active_node_hb(cls, request, node):
        """刷新活跃节点心跳
        """
        ip = NodeManager.get_node_ip(request)
        try:
            models.Node.everything.filter(id=node.id).update(last_beat_time=now(), addr=ip, modifier=request.user)
            if node.enabled == models.Node.EnabledEnum.OFFLINE:
                models.Node.objects.filter(id=node.id).update(enabled=models.Node.EnabledEnum.ACTIVE)
        except Exception as err:
            logger.exception("[Node: %s] refresh node heartbeat exception: %s" % (node, err))
        return {"id": node.id}

    @classmethod
    def get_active_node_num(cls):
        """获取活跃节点数
        """
        return models.Node.objects.filter(enabled=models.Node.EnabledEnum.ACTIVE).count()

    @classmethod
    def validate_node_org(cls, user, org_sid):
        """校验节点指定的团队信息
        """
        if not org_sid and user.is_superuser:
            return True
        return OrganizationManager.check_user_org_perm(user, org_sid=org_sid)

    @classmethod
    def register_node(cls, request, data):
        """注册节点
        """
        try:
            node = models.Node.everything.get(uuid=data['uuid'])
            NodeManager.restore_existed_node(request, node, data)
        except models.Node.DoesNotExist:
            node = NodeManager.create_new_node(request, data)
            if data.get("org_sid"):
                logger.info("[Node: %s] 团队节点需手动初始化" % node)
            else:
                NodeManager.init_node_config(node, data.get("os_info"), data.get("tag"))
        return {'id': node.id}

    @classmethod
    def restore_existed_node(cls, request, node, data):
        """恢复已存在的节点
        """
        if node.enabled == models.Node.EnabledEnum.DISABLED:
            return node
        if node.deleted_time:
            node.undelete()
            node.deleter = None
            node.deleted_time = None
        if not node.tag and data.get("tag"):
            node.tag = data.get("tag")
            node.save(user=request.user)
        # 回收node相应的task
        task_ids = list(Task.objects.filter(node=node, state=Task.StateEnum.RUNNING).values_list("id", flat=True))
        Task.objects.filter(id__in=task_ids).update(
            state=Task.StateEnum.WAITING, result_msg="Switch to waiting because node was just registered")
        TaskProcessRelation.objects.filter(node=node, state=TaskProcessRelation.StateEnum.RUNNING) \
            .update(state=TaskProcessRelation.StateEnum.WAITING)
        node.enabled = models.Node.EnabledEnum.ACTIVE
        node.state = models.Node.StateEnum.FREE
        node.save(user=request.user)
        return node

    @classmethod
    def create_new_node(cls, request, data):
        """创建新的节点
        """
        ip = cls.get_node_ip(request)
        logger.info("[Node] create new node, ip: %s, data: %s" % (ip, data))
        if request.user.is_superuser is True:
            enabled = models.Node.EnabledEnum.ACTIVE
        else:
            enabled = models.Node.EnabledEnum.DISABLED
        node = models.Node(
            name=data['uuid'],
            addr=ip,
            enabled=enabled,
            last_beat_time=now(),
            uuid=data['uuid'],
            manager=request.user,
            org_sid=data.get("org_sid")
        )
        node.save(user=request.user)
        return node

    @classmethod
    def init_node_config(cls, node, node_os=None, node_tag=None):
        """初始化节点配置（关联工具和标签）
        """

        if not node_os:
            node_os = ""
        if node_tag:
            node.exec_tags.add(node_tag)
            tag = node_tag
        elif "linux" in node_os.lower():
            tag = models.ExecTag.objects.filter(name__contains="Linux", public=True).first()
            node.exec_tags.add(tag)
        elif "windows" in node_os.lower():
            tag = models.ExecTag.objects.filter(name__contains="Windows", public=True).first()
            node.exec_tags.add(tag)
        elif "mac" in node_os.lower() or "darwin" in node_os.lower():
            tag = models.ExecTag.objects.filter(name__contains="Mac", public=True).first()
            node.exec_tags.add(tag)
        else:
            logger.warning("[Node: %s] 无法识别当前操作系统[%s]，默认设置为Linux公共标签" % (node.addr, node_os))
            tag = models.ExecTag.objects.filter(name__contains="Linux", public=True).first()
            node.exec_tags.add(tag)

        if not models.TagToolProcessRelation.objects.first():
            """当未匹配到标签进程时，自动选择公开工具进行配置
            """
            if tag.public is True:
                for checktool in scan_conf_models.CheckTool.objects.all():
                    if not checktool.is_public() or (checktool.license and "商业" in checktool.license):
                        continue
                    processes = scan_conf_models.Process.objects.filter(checktool=checktool)
                    for process in processes:
                        models.NodeToolProcessRelation.objects.get_or_create(node=node, checktool=checktool,
                                                                             process=process)
        else:
            all_processes = cls.get_support_process_relations(cls.get_all_processes(), tag)
            cls.update_node_processes(node, all_processes)

    @classmethod
    def batch_update_node_processes(cls, nodes, data):
        """批量更新节点进程
        """
        for node in nodes:
            cls.update_node_processes(node, data)

    @classmethod
    def batch_update_node_detail(cls, nodes, data):
        """批量更新节点信息
        包含相关责任人、节点标签等
        """
        for node in nodes:
            if data.get("related_managers") is not None:
                node.related_managers.set(data.get("related_managers"))
            if data.get("exec_tags") is not None:
                node.exec_tags.set(data.get("exec_tags"))
            if data.get("enabled") is not None:
                node.enabled = data["enabled"]
                node.save()

    @classmethod
    def get_checktool_dict(cls):
        """获取检查工具映射
        """
        checktool_dict = {
            checktool.name: checktool for checktool in scan_conf_models.CheckTool.objects.all()}
        return checktool_dict

    @classmethod
    def get_process_dict(cls):
        """获取进程映射
        """
        process_dict = {
            process.name: process for process in scan_conf_models.Process.objects.all()}
        return process_dict

    @classmethod
    def get_all_processes(cls):
        """获取所有工具进程
        """
        all_processes = {}
        for tool_process in scan_conf_models.ToolProcessRelation.objects.all():
            processes = all_processes.get(tool_process.checktool.name, {})
            processes.update({tool_process.process.name: {"supported": False}})
            all_processes.update({tool_process.checktool.name: processes})
        return all_processes

    @classmethod
    def get_support_process_relations(cls, all_processes, obj):
        """获取已支持的进程关系数据
        """
        if isinstance(obj, models.ExecTag):
            fields = {"tag": obj}
            relation_cls = models.TagToolProcessRelation
        elif isinstance(obj, models.Node):
            fields = {"node": obj}
            relation_cls = models.NodeToolProcessRelation
        else:
            return
        for process_relation in relation_cls.objects.filter(**fields):
            try:
                all_processes[process_relation.checktool.name][
                    process_relation.process.name]["supported"] = True
                all_processes[process_relation.checktool.name][
                    process_relation.process.name]["id"] = process_relation.id
            except Exception as e:  # NOCA:broad-except(可能存在多种异常)
                logger.exception("[Tool: %s][Process: %s] err: %s" % (
                    process_relation.checktool.name, process_relation.process.name, e))
        return all_processes

    @classmethod
    def update_process_relations(cls, data, obj):
        """更新指定对象的进程映射关系
        """
        if isinstance(obj, models.ExecTag):
            fields = {"tag": obj}
            relation_cls = models.TagToolProcessRelation
        elif isinstance(obj, models.Node):
            fields = {"node": obj}
            relation_cls = models.NodeToolProcessRelation
        else:
            return

        delete_ids = {}
        checktool_dict = cls.get_checktool_dict()
        process_dict = cls.get_process_dict()
        for checktool__name, process_relations in data.items():
            checktool = checktool_dict.get(checktool__name)
            if checktool:
                for process__name, setting in process_relations.items():
                    process = process_dict.get(process__name)
                    if setting["supported"]:
                        if process and not relation_cls.objects.filter(
                                checktool=checktool, process=process, **fields):
                            relation_cls.objects.create(checktool=checktool, process=process, **fields)
                    else:  # not supported
                        relations = relation_cls.objects.filter(checktool=checktool, process=process, **fields).first()
                        if relations:
                            delete_ids[relations.id] = {"tool": checktool.name, "process": process.name}
        logger.info("%s delete node tool process: %s" % (fields, list(delete_ids.values())))
        relation_cls.objects.filter(id__in=list(delete_ids.keys())).delete()

    @classmethod
    def update_node_processes(cls, node, data):
        """更新节点进程
        """
        cls.update_process_relations(data, node)

    @classmethod
    def update_tag_processes(cls, tag, data):
        """更新标签进程
        """
        cls.update_process_relations(data, tag)
