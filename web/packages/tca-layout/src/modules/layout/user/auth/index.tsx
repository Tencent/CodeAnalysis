// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { Layout, Button, Row, Col, Tag, message } from 'coding-oa-uikit';
import Plus from 'coding-oa-uikit/lib/icon/Plus';

// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';
import { AUTH_TYPE } from '@src/utils/constant';
import { gScmAccounts, getSSHInfo, delScmAccount, delSSHInfo } from '@src/services/user';

import AuthModal from './auth-modal';
import AuthTable from './auth-table';
import s from '../style.scss';

const { Content } = Layout;

const Auth = () => {
  const [dataSource, setDataSource] = useState<any>([]);
  const [visible, setVisible] = useState(false);
  const [visibleDel, setVisibleDel] = useState(false);
  const [curAuthInfo, setCurAuthInfo] = useState<any>({});
  const [authinfo, setAuthinfo] = useState(null);
  const [reload, setReload] = useState(false);

  /**
     * 获取全部凭证
     */
  useEffect(() => {
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      gScmAccounts().then(r => r.results || []),
    ]).then((result) => {
      setDataSource([
        ...(result[0] || []).map((item: any) => ({ ...item, auth_type: AUTH_TYPE.SSH })),
        ...(result[1] || []).map((item: any) => ({ ...item, auth_type: AUTH_TYPE.HTTP })),
      ]);
    });
  }, [reload]);

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
    </Content>
  );
};

export default Auth;
