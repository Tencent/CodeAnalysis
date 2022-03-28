# -*- coding: utf-8 -*-
# Copyright (c) 2021-2022 THL A29 Limited
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
            logger.exception("[Node: %s] refresh node heartbeat exception: %s" % err)
        return {"id": node.id}

    @classmethod
    def get_active_node_num(cls):
        """获取活跃节点数
        """
        return models.Node.objects.filter(enabled=models.Node.EnabledEnum.ACTIVE).count()

    @classmethod
    def register_node(cls, request, data):
        """注册节点
        """
        try:
            node = models.Node.everything.get(uuid=data['uuid'])
            NodeManager.restore_existed_node(request, node, data)
        except models.Node.DoesNotExist:
            node = NodeManager.create_new_node(request, data)
            NodeManager.init_node_config(node, data.get("os_info"))
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
        logger.info("[Node] create new node, ip: %s" % ip)
        node = models.Node(
            name=data['uuid'],
            addr=ip,
            enabled=models.Node.EnabledEnum.DISABLED,
            last_beat_time=now(),
            uuid=data['uuid'],
            tag=data.get("tag"),
            manager=request.user,
        )
        node.save(user=request.user)
        return node

    @classmethod
    def init_node_config(cls, node, node_os=None):
        """初始化节点配置（关联工具和标签）
        """
        for checktool in scan_conf_models.CheckTool.objects.all():
            if not checktool.is_public() or (checktool.license and "商业" in checktool.license):
                continue
            processes = scan_conf_models.Process.objects.filter(checktool=checktool)
            for process in processes:
                models.NodeToolProcessRelation.objects.get_or_create(node=node, checktool=checktool, process=process)
        if not node_os:
            node_os = ""
        if "linux" in node_os.lower():
            linux_tag = models.ExecTag.objects.filter(name__contains="Linux", public=True).first()
            node.exec_tags.add(linux_tag)
        elif "windows" in node_os.lower():
            windows_tag = models.ExecTag.objects.filter(name__contains="Windows", public=True).first()
            node.exec_tags.add(windows_tag)
        elif "mac" in node_os.lower() or "darwin" in node_os.lower():
            mac_tag = models.ExecTag.objects.filter(name__contains="Mac", public=True).first()
            node.exec_tags.add(mac_tag)
        else:
            logger.warning("[Node: %s] 无法识别当前操作系统[%s]，默认设置为Linux公共标签" % (node.addr, node_os))
            linux_tag = models.ExecTag.objects.filter(name__contains="Linux", public=True).first()
            node.exec_tags.add(linux_tag)

    @classmethod
    def update_node_processes(cls, node, data):
        """更新节点进程
        """
        delete_ids = []
        checktool_dict = {
            checktool.name: checktool for checktool in scan_conf_models.CheckTool.objects.all()}
        process_dict = {
            process.name: process for process in scan_conf_models.Process.objects.all()}
        for checktool__name, process_relations in data.items():
            checktool = checktool_dict.get(checktool__name)
            if checktool:
                for process__name, setting in process_relations.items():
                    process = process_dict.get(process__name)
                    if setting["supported"]:
                        if process and not models.NodeToolProcessRelation.objects.filter(node=node, checktool=checktool,
                                                                                         process=process):
                            models.NodeToolProcessRelation.objects.create(
                                node=node, checktool=checktool, process=process)
                    else:  # not supported
                        relations = models.NodeToolProcessRelation.objects.filter(
                            node=node, checktool=checktool, process=process).first()
                        if relations:
                            delete_ids.append(relations.id)
        models.NodeToolProcessRelation.objects.filter(
            id__in=delete_ids).delete()
