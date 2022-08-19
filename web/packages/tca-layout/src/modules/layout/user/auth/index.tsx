// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { Layout, Button, Row, Col, Tag, message } from 'coding-oa-uikit';
import Plus from 'coding-oa-uikit/lib/icon/Plus';
import { get, filter } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';
import { AUTH_TYPE, DEFAULT_SCM_PLATFORM } from '@src/utils/constant';
import { gScmAccounts, getSSHInfo, delScmAccount, delSSHInfo, getOAuthStatus, delOAuthStatus, getPlatformStatus } from '@src/services/user';

import AuthModal from './auth-modal';
import AuthTable from './auth-table';
import OAuthTable from './oauth-table';
import s from '../style.scss';

const { Content } = Layout;

const Auth = () => {
  const [oauthData, setOAuthData] = useState<any>([]);
  const [curOAuthData, setCurOAuthData] = useState<any>({});
  const [dataSource, setDataSource] = useState<any>([]);
  const [visible, setVisible] = useState<boolean>(false);
  const [visibleDel, setVisibleDel] = useState<boolean>(false);
  const [visibleCancel, setVisibleCancel] = useState<boolean>(false);
  const [curAuthInfo, setCurAuthInfo] = useState<any>({});
  const [authinfo, setAuthinfo] = useState<any>(null);
  const [reload, setReload] = useState<boolean>(false);

  /**
     * 获取全部凭证
     */
  useEffect(() => {
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      gScmAccounts().then(r => r.results || []),
      getPlatformStatus().then(r => r || []),
      getOAuthStatus().then(r => r || []),
    ]).then((result) => {
      setDataSource([
        ...(result[0] || []).map((item: any) => ({ ...item, auth_type: AUTH_TYPE.SSH })),
        ...(result[1] || []).map((item: any) => ({ ...item, auth_type: AUTH_TYPE.HTTP })),
      ]);
      setOAuthData(
        filter(
          DEFAULT_SCM_PLATFORM.map((item:any)=>({ 
            ...item, 
            oauth_status: get(result[3], item.scm_platform_name, [false]),
            platform_status: get(result[2], item.scm_platform_name, [false]),
          })),
          'platform_status'
        )
      );
    });
  }, [reload]);

  /**
     * 监听OAuth事件
     */
  useEffect(() => {
    window.addEventListener("message", receiveOAuthStatus, false);
    return () => {
      window.removeEventListener('message',receiveOAuthStatus);
    };
  }, []);

  /**
     * 获取OAuth凭证
     */
  const updateOAuthList = () => {
    Promise.all([
      getPlatformStatus().then(r => r || []),
      getOAuthStatus().then(r => r || []),
    ]).then((result) => {
      setOAuthData(
        filter(
          DEFAULT_SCM_PLATFORM.map((item:any)=>({ 
            ...item, 
            oauth_status: get(result[1], item.scm_platform_name, [false]),
            platform_status: get(result[0], item.scm_platform_name, [false]),
          })),
          'platform_status'
        )
      );
    });
  };

  /**
     * 创建/更新凭证信息
     * @param authinfo 凭证信息
     */
  const onCreateOrEditHandle = (authinfo: any = null) => {
    setAuthinfo(authinfo);
    setVisible(true);
  };

  /**
     * 删除当前凭证
     * @param curAuthInfo 当前凭证信息
     */
  const onDelAuthHandle = (curAuthInfo: any) => {
    const promise = curAuthInfo.auth_type === AUTH_TYPE.HTTP
      ? delScmAccount(curAuthInfo.id)
      : delSSHInfo(curAuthInfo.id);
    promise.then(() => {
      message.success(t('已删除凭证'));
      setVisibleDel(false);
      setReload(!reload);
    });
  };

  /**
     * 接收OAuth授权结果
     */
  const receiveOAuthStatus = (event: any) => {
    const curLocation = window.location;
    if (event.origin === curLocation.origin) {
      if(event.data === 'oauth succeeded') {
        message.success('授权成功');
        updateOAuthList();
      } else if (event.data === 'oauth failed') {
        message.error('授权失败');
      }
    }
  }

  /**
     * 计算OAuth窗口居中弹出位置
     */
  const getWindowSize = () => {
    const width = 800;
    const height = 800;
    const top = window.innerHeight > height ? (window.innerHeight-height)/2 : 0;
    const left = window.innerWidth > width ? (window.innerWidth -width)/2 : 0;
    return `top=${top},left=${left},width=${width},height=${height}`;
  }

  /**
     * 首次授权OAuth
     * @param oauthInfo 选中OAuth平台信息
     */
  const onOAuthStart = (oauthInfo: any) => {
    const winRef = window.open('',"oauthWindow",getWindowSize());
    getOAuthStatus({scm_platform_name: oauthInfo?.scm_platform_name}).then((res)=>{
      winRef.location = res?.git_auth_url;
    }).catch(()=>{
      winRef.close();
      message.error('平台暂未配置OAuth应用，无法去授权，请联系管理员。');
    });
  };

  /**
   * 重新授权OAuth
   * @param oauthInfo 选中OAuth平台信息
   */
  const onOAuthUpdate = (oauthInfo: any) => {
    const winRef = window.open('',"oauthWindow",getWindowSize());
    getOAuthStatus({scm_platform_name: oauthInfo?.scm_platform_name}).then((res)=>{
      winRef.location = res?.git_auth_url;
    }).catch(()=>{
      winRef.close();
      message.error(t('更新授权失败'));
    });
  };

  /**
     * 尝试解除OAuth授权，弹出提示
     * @param oauthInfo 选中OAuth平台信息
     */
  const onOAuthDelStart = (oauthInfo: any) => {
    setVisibleCancel(true);
    setCurOAuthData(oauthInfo);
  };

  /**
     * 解除OAuth授权
     * @param oauthInfo 选中OAuth平台信息
     */
  const onOAuthDel = (oauthInfo: any) => {
    delOAuthStatus({scm_platform_name: oauthInfo?.scm_platform_name}).then(()=>{
      message.success(t('已解除授权'));
      updateOAuthList();
    }).catch(()=>{
      message.error(t('无法解除授权'));
    }).finally(()=>{
      setVisibleCancel(false);
    });
  };

  return (
    <Content className="pa-lg">
      <div className={s.header}>
        <Row>
          <Col flex="auto">
            <h3 className=" fs-18">{t('凭证管理')}</h3>
          </Col>
          <Col flex="200px" className=" text-right">
            <Button
              type="primary"
              icon={<Plus />}
              onClick={() => onCreateOrEditHandle()}
            >
              {t('录入凭证')}
            </Button>
          </Col>
        </Row>
        <p className=" text-grey-7">
          {t('录入后，仓库登记、分支项目等模块可直接选择凭证，无需重复填写。')}
        </p>
      </div>
      {oauthData.length > 0 && <OAuthTable
        dataSource={oauthData}
        onOAuth={onOAuthStart}
        onUpdate={onOAuthUpdate}
        onDel={onOAuthDelStart}
      />}
      <AuthTable
        dataSource={dataSource}
        onEdit={onCreateOrEditHandle}
        onDel={(authinfo) => {
          setCurAuthInfo(authinfo);
          setVisibleDel(true);
        }}
      />
      <AuthModal
        visible={visible}
        authinfo={authinfo}
        onOk={() => {
          setVisible(false);
          setReload(!reload);
        }}
        onCancel={() => setVisible(false)}
      />
      <DangerModal
        title={t('删除凭证')}
        visible={visibleDel}
        onCancel={() => setVisibleDel(false)}
        onOk={() => onDelAuthHandle(curAuthInfo)}
        content={
          <div>
            {t('确认删除凭证')}{' '}
            <Tag color="default">
              {curAuthInfo.auth_type === AUTH_TYPE.HTTP
                ? curAuthInfo.scm_username
                : curAuthInfo.name}
            </Tag>{' '}
            {t('？')}
          </div>
        }
      />
      <DangerModal
        title={t('取消Git OAuth授权')}
        visible={visibleCancel}
        onCancel={() => setVisibleCancel(false)}
        onOk={() => onOAuthDel(curOAuthData)}
        okText={t('确认取消')}
        content={
          <div>Git Oauth授权能够免密执行腾讯代码分析代码分析，提供更快的分析速度，确定取消Git OAuth授权?</div>
        }
      />
    </Content>
  );
};

export default Auth;
