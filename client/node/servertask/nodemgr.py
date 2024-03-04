# -*- encoding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""
节点管理,包括节点注册,心跳和状态上报
"""

import threading
import time
import psutil
import uuid
import sys
import socket

from node import app
from platform import platform

from util.logutil import LogPrinter


class NodeMgr(object):
    """本地节点管理"""

    def get_docker_uuid(self, create_from, tag):
        """如果从docker创建，获取到docker的主机名，与标签一起拼接成为节点唯一标识NODE_UUID"""
        if create_from and "docker" == create_from:
            host_name = socket.gethostname()
            return f"{tag}-{host_name}"
        return None

    def register_node(self, server, tag=None, org_sid=None, create_from=None):
        '''用本地node_uuid向server注册，获取server给的node_id。
        如果node_id和本地存储node_id不一致，则抛出异常。
        '''
        if not tag:
            tag = app.settings.OS_TAG_MAP[sys.platform]
        node_uuid = app.persist_data.get('NODE_UUID')
        if not node_uuid:
            node_uuid = self.get_docker_uuid(create_from, tag)
            if not node_uuid:
                node_uuid = uuid.uuid1().hex
            app.persist_data['NODE_UUID'] = node_uuid

        data = {
            "uuid": node_uuid,
            "tag": tag,
            "os_info": app.settings.PLATFORMS[sys.platform],
            "org_sid": org_sid  # 为空时，表示为公共节点，不为空时，表示指定团队的节点
        }
        if create_from:
            data["create_from"] = create_from
        node_id = server.register(data)
        LogPrinter.info('node(%s) registered in server node id:%s', node_uuid, node_id)
        app.persist_data['NODE_ID'] = node_id


class HostNetMgr(object):
    """机器网卡信息管理"""
    def get_net_if_addr(self):
        """获取多网卡 mac 和 ip 信息"""
        result = []
        net_addrs = psutil.net_if_addrs()
        for adapter, snic_list in net_addrs.items():
            mac = None  # '无 mac 地址'
            ipv4 = None  # '无 ipv4 地址'
            ipv6 = None  # '无 ipv6 地址'
            for snic in snic_list:
                if snic.family.name in ['AF_LINK', 'AF_PACKET']:
                    mac = snic.address
                if snic.family.name == "AF_INET":
                    ipv4 = snic.address
                if snic.family.name == "AF_INET6":
                    ipv6 = snic.address
            result.append({
                'adapter': adapter,
                "mac": mac,
                'ipv4': ipv4,
                'ipv6': ipv6
            })
        return result

    def get_host_ip(self):
        """获取本机ip"""
        try:
            net_info_list = self.get_net_if_addr()
            for net_info in net_info_list:
                mac = net_info["mac"]
                ipv4 = net_info["ipv4"]
                if mac and ipv4 and ipv4 != "127.0.0.1":  # 有mac地址和ipv4地址，才算获取到当前在用的ip
                    return ipv4
        except Exception as err:
            LogPrinter.error("get host ip error: %s" % str(err))
            return ""


class HeartBeat(object):
    """
    心跳上报
    """
    def __init__(self, node_server):
        """

        :param node_server: 上报api实例
        :return:
        """
        self._server = node_server
        self._beat_interval = 8  # sec 心跳上传的频率

    def _thread_beat(self):
        """
        心跳上报线程
        """
        while True:
            host_ip = HostNetMgr().get_host_ip()
            data = {"puppy_ip": host_ip}
            # LogPrinter.info(f">>> data: {data}")
            try:
                self._server.heart_beat(data)
            except Exception as err:
                LogPrinter.exception(f"heart beat error: {str(err)}")
            time.sleep(self._beat_interval)

    def start(self):
        beat_thread = threading.Thread(target=self._thread_beat)
        beat_thread.daemon = True
        beat_thread.start()
        LogPrinter.info("heart beat thread is started.")


class NodeStatusMonitor(object):
    """
    当前机器的状态信息上报，包括cup，内存，硬盘（当前文件所在盘）等
    """
    def __init__(self, node_server):
        """

        :param node_server: 上报api实例
        :return:
        """
        self._server = node_server
        self._profiling_interval = 2 * 60 # sec 状态上报的频率

    def _get_status_info(self):
        '''
        返回当前机器的状态信息，包括cup，内存，硬盘（当前文件所在盘）等
        '''
        cpu_num = psutil.cpu_count()
        cpu_usage = int(psutil.cpu_percent(interval=1.0))
        # return staticstics about system memory usage as a nametuple including the following fields(unit:bytes)
        # (total, available, percent, used, free)
        memory_info = psutil.virtual_memory()
        memory_space = memory_info.total
        memory_free_space = memory_info.available
        # return staticstics about disk usage as a nametuple including the following fields(unit:bytes)
        # (total, used, free, percent)
        disk_info = psutil.disk_usage(app.settings.BASE_DIR)
        hdrive_space = disk_info.total
        hdrive_free_space = disk_info.free
        os = platform()
        status_info = {"cpu_num": cpu_num, "cpu_usage": cpu_usage,
                       "mem_space":str(memory_space), "mem_free_space": str(memory_free_space),
                       "hdrive_space": str(hdrive_space), "hdrive_free_space": str(hdrive_free_space),
                       "network_latency": 0, "os": os}
        return status_info

    def _thread_update_status(self):
        """
        机器状态上报线程
        """
        while True:
            self._server.update_status(self._get_status_info())
            time.sleep(self._profiling_interval)

    def start(self):
        status_thread = threading.Thread(target=self._thread_update_status)
        status_thread.daemon = True
        status_thread.start()
        LogPrinter.info("node status profiling thread is started.")