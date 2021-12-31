# -*- coding: utf-8 -*-
"""
基础 接口模块
"""

from rest_framework.views import APIView
from rest_framework.response import Response


class BaseApiView(APIView):
    """基础接口，用于首页
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """获取基础页数据
        """
        return Response(data={"msg": "Weclome to CodeDog FTP Server"})
