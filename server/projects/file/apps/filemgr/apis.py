# -*- coding: utf-8 -*-
# Copyright (c) 2021-2024 THL A29 Limited
#
# This source code file is made available under MIT License
# See LICENSE for details
# ==============================================================================

"""文件上传接口

存储引擎：本地存储/COS/minio等（灵活扩展）
"""
import base64
import logging
import os
from urllib import parse

from django.db import IntegrityError
from django.http import HttpResponse, StreamingHttpResponse
from rest_framework.response import Response
from rest_framework.status import HTTP_500_INTERNAL_SERVER_ERROR
from rest_framework.views import APIView

from apps.filemgr import models, core
from apps.filemgr.permissions import PermissionCheckMixIn
from apps.filemgr.utils import format_file, CDFileUploadParser
from utils import error
from utils.file_storage import storage_client

logger = logging.getLogger(__name__)


class AuthAPIView(APIView, PermissionCheckMixIn):

    def _base_check(self, request, bucket, dir_path, file_name):
        """基础检查操作
        """
        # 获取对应的app_unit
        app_unit = self._format_app_unit_response(bucket, dir_path)

        # 检查用户对当前app/type是否有读权限
        username = request.user.username
        self._format_user_permission_response(app_unit, username, ['rw'])

        # 检查文件是否存在
        self._format_file_exist_response(app_unit, file_name)
        return app_unit

    @staticmethod
    def _format_auth_response(method, app, dir_path, file_name, params, **kwargs):
        host, path = storage_client.format_host_path(app, dir_path, file_name)
        try:
            auth_headers = storage_client.format_auth(
                method.lower(), path, params, {'host': host}, 
                content_sha256=kwargs.get("content_sha256"))
        except Exception as e:
            if "NoSuchBucket" in str(e):
                result, msg = storage_client.create_bucket(app)
                if not (result or 'bucket already exist' in msg):
                    raise error.QFSRequestError(msg, error.BUCKET_CREATE_FAIL)
            raise error.QFSParamConfigError('Url invalid. %s ' % repr(e))

        response = HttpResponse('')
        response['req_host'] = host
        response['req_path'] = storage_client.quote_lower(path)

        for key, value in auth_headers.items():
            response[key] = value
        return response

    def put(self, request, uri):
        # 解析bucket，dir_path，file_name
        bucket, dir_path, file_name = self._format_file_response(uri)
        logger.info("uri: %s ==> %s, %s, %s" % (uri, bucket, dir_path, file_name))
        # 先检查是否有bucket了，如果没有bucket则需要通知cos去创建
        bucket_count = models.AppUnit.objects.filter(bucket=bucket).count()
        if bucket_count == 0:
            result, msg = storage_client.create_bucket(bucket)
            if not (result or 'bucket already exist' in msg):
                # 如果bucket已存在，也算创建成功，否者抛出异常
                raise error.QFSRequestError(msg, error.BUCKET_CREATE_FAIL)

        # 创建好bucket后，检查当前app/type是否有权限
        username = request.user.username
        app_unit, is_create = None, True
        try:
            app_unit, is_create = models.AppUnit.objects.get_or_create(
                name='%s/%s' % (bucket, dir_path), bucket=bucket, defaults={'creator': username})
        except IntegrityError:
            # 防止并发竞争，在name上增加唯一索引
            pass

        if (not is_create) and (app_unit.creator != username and app_unit.other_permission != 'rw'):
            # 如果是已有的app/type，先检查权限看当前用户是否可以写
            raise error.QFSUnitForbidden('当前用户没有%s/%s目录下的写权限' % (bucket, dir_path))

        # 有权限，则组装auth，允许上传
        response = self._format_auth_response(
            request.method, bucket, dir_path, file_name, request.GET,
            content_sha256=request.META.get("HTTP_CONTENT_SHA256") or request.META.get("HTTP_FTP_SHA256"))
        return response

    def get(self, request, uri):
        # 解析bucket，dir_path，file_name
        bucket, dir_path, file_name = self._format_file_response(uri)
        logger.info("uri: %s ==> %s, %s, %s" % (uri, bucket, dir_path, file_name))
        self._base_check(request, bucket, dir_path, file_name)
        response = self._format_auth_response(
            request.method, bucket, dir_path, file_name, request.GET)
        return response

    def delete(self, request, uri):
        # 解析bucket，dir_path，file_name
        bucket, dir_path, file_name = self._format_file_response(uri)
        self._base_check(request, bucket, dir_path, file_name)

        response = self._format_auth_response(
            request.method, bucket, dir_path, file_name, request.GET)
        return response


class CDLocalStorageView(AuthAPIView):
    parser_classes = [CDFileUploadParser]

    def check_file_body(self, request):
        """检查是否有上传文件
        """
        if not request.data.get("file"):
            logger.info("request.data %s" % request.data)
            raise error.QFSFileUploadError("上传失败")

    def put(self, request, uri):
        """
        文件上传
        """
        # 解析bucket，dir_path，file_name
        username = request.user.username
        bucket, dir_path, file_name = self._format_file_response(uri)
        logger.info("[User: %s] upload file, bucket: %s, dir: %s, file: %s" % (
            username, bucket, dir_path, file_name))
        self.check_file_body(request)

        core.FileUploadHandler.create_bucket(bucket)
        # 创建好bucket后，检查当前app/type是否有权限
        core.FileUploadHandler.check_bucket_write_permission(bucket, dir_path, username)

        # 有权限，则允许上传
        is_uploaded, msg, content_md5 = core.FileUploadHandler.save_file_to_local(
            request.data['file'], bucket, dir_path, file_name)
        logger.info("Current file md5: %s" % content_md5)
        if is_uploaded:
            if not core.FileHandler.check_content_md5(request, content_md5):
                raise error.QFSFileUploadError("上传失败，文件MD5值与头部MD5值不一致")
            core.FileHandler.execute_file_action(request, bucket, dir_path, file_name)
            return Response({"msg": "Upload success"})
        else:
            raise error.QFSFileUploadError("上传失败")

    def _generate_streaming_response(self, msg, file_name, content_md5, size):
        """生成流式响应
        """
        response = StreamingHttpResponse(msg)
        response['Content-Length'] = size
        response['Content-MD5'] = content_md5
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="%s"' % os.path.split(file_name)[1]
        return response

    def get(self, request, uri):
        """
        文件下载
        """
        # 解析bucket，dir_path，file_name
        bucket, dir_path, file_name = self._format_file_response(uri)
        logger.info("[User: %s] get file, bucket: %s, dir: %s, file: %s" % (
            request.user, bucket, dir_path, file_name))
        self._base_check(request, bucket, dir_path, file_name)

        file_ins = core.FileDownloadHandler.check_file_exist(bucket, dir_path, file_name)
        if not file_ins:
            raise error.QFSFileNotExistdError("文件不存在")
        is_downloaded, msg, size = core.FileDownloadHandler.download_from_local(bucket, dir_path, file_name)
        if is_downloaded:
            download_file = core.FileHandler.execute_file_action(request, bucket, dir_path, file_name)
            return self._generate_streaming_response(msg, file_name, download_file.content_md5, size)
        raise error.QFSFileDownloadError("下载失败")

    def delete(self, request, uri):
        """
        删除文件
        """
        # 解析bucket，dir_path，file_name
        bucket, dir_path, file_name = self._format_file_response(uri)
        self._base_check(request, bucket, dir_path, file_name)
        is_deleted, msg = storage_client.delete_file(bucket, '%s/%s' % (dir_path, file_name))
        if is_deleted:
            core.FileHandler.execute_file_action(request, bucket, dir_path, file_name)
            return Response({'msg': "delete success"})
        else:
            raise error.QFSFileDeleteError('删除失败')


class FileLogAPIView(APIView):
    """日志记录接口
    """

    def _base(self, request):
        """
        """
        # 请求未成功时，不做任何记录
        request_pre_status = request.META.get('HTTP_PRE_STATUS', '')
        if request_pre_status != '200':
            logger.debug("[User: %s] current request pre status: %s" % (request.user, request_pre_status))
            return Response('')

        uri = request.META.get('HTTP_PRE_URI')
        if not uri:
            logger.debug("[User: %s] current request pre uri was none" % request.user)
            return Response('')

        # uri 为用户第一次的请求，因此还会有files的前缀
        uri = uri.split('files', 1)[-1]
        # uri中如果包含中文，则此时会为quote后的内容，需要转为quote前的utf-8内容
        try:
            uri = parse.unquote(uri)
        except Exception as err:
            logger.exception("[User: %s] parse url failed: %s" % (request.user, err))
            pass

        try:
            bucket, dir_path, file_name = format_file(uri)
            logger.info("[User: %s] execute file action, uri: %s => [Bucket: %s, Dir: %s, File: %s]" % (
                request.user, uri, bucket, dir_path, file_name))
            core.FileHandler.execute_file_action(request, bucket, dir_path, file_name)
        except error.QFSRequestError:
            # 参数不合法的请求可忽略
            pass

        return Response('')

    def get(self, request):
        return self._base(request)

    def put(self, request):
        return self._base(request)

    def delete(self, request):
        return self._base(request)


class AppUnitConfigAPIView(APIView):
    """App配置更新接口
    """

    def put(self, request, bucket, dir_path):
        bucket = bucket.lower()
        dir_path = dir_path.lower()

        try:
            app_unit = models.AppUnit.objects.get(name='%s/%s' % (bucket, dir_path))
        except models.AppUnit.DoesNotExist:
            raise error.QFSUnitNotFound('当前存储单元%s/%s不存在' % (bucket, dir_path))

        if app_unit.creator != request.user.username:
            raise error.QFSUnitForbidden('当前用户没有%s/%s目录下的写权限' % (bucket, dir_path))

        if 'retention' in request.data:
            # 修改文件过期时间
            overdue_time = request.data['retention']
            if not overdue_time.isdigit():
                raise error.QFSParamConfigError('文件有效时长格式错误，请输入以天为单位的非负整数')
            app_unit.expired = overdue_time
            app_unit.save()

        if 'acl_other' in request.data:
            # 修改其他用户权限
            other_permission = request.POST['acl_other']
            if other_permission not in ['', 'r', 'rw']:
                raise error.QFSParamConfigError('文件权限格式错误，文件权限可选范围：空字符串，r，rw')

            app_unit.other_permission = other_permission
            app_unit.save()
        return Response({"msg": "成功更新App配置"})


class ErrorCallbackAPIView(APIView):
    """错误回调接口
    """

    def get(self, request):
        err_type = request.META.get('HTTP_ERR_TYPE')
        err_msg = base64.b64decode(request.META.get('HTTP_ERR_MSG', ''))
        logger.info("[ErrType: %s] error mgs: %s" % (err_type, err_msg))
        result = {}
        if not err_type:
            # 如果是前端直接请求过来的，则返回 200，避免框架当成异常处理了
            return Response(result)

        result["Err-type"] = err_type
        if err_msg:
            result['Err-msg'] = err_msg
        status_code = error.ERROR_CODE.get(err_type, HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(result, status_code)
