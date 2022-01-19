// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import CopyToClipboard from 'react-copy-to-clipboard';
import { Layout, Row, Col, Input, Button, message, Divider, Tooltip, Tag } from 'coding-oa-uikit';
import Copy from 'coding-oa-uikit/lib/icon/Copy';
import Sync from 'coding-oa-uikit/lib/icon/Sync';

// 项目内
import { t } from '@src/i18n/i18next';
import { getUserToken, putUserToken } from '@src/services/user';
import { useStateStore } from '@src/context/store';
import { API_DOC_PATH } from '@src/utils/getRoutePath';

// 模块内
import s from '../style.scss';

const { Content } = Layout;

const LEVEL_ENUM = {
  NORMAL: 1,
  VIP: 2,
  SUPER_VIP: 3,
};

const Token = () => {
  const { userinfo } = useStateStore();
  const [token, setToken] = useState('');

  useEffect(() => {
    if (userinfo.level === LEVEL_ENUM.SUPER_VIP) {
      getUserToken().then((response) => {
        setToken(response.token);
      });
    }
  }, [userinfo.level]);

  const onUpdateTokenHandle = () => {
    putUserToken().then((response) => {
      message.success('已刷新令牌');
      setToken(response.token);
    });
  };

  return (
    <Content className="pa-lg">
      <div className={s.header}>
        <Row>
          <Col flex="auto">
            <h3 className=" fs-18">{t('个人令牌')}</h3>
          </Col>
          <Col flex="200px" className=" text-right" />
        </Row>
      </div>
      <div className="my-md">
        个人访问令牌可用于访问{' '}
        <a href={API_DOC_PATH} target="_blank" rel="noreferrer">
          腾讯云代码分析 API
        </a>
        ，仅<Tag className="ml-sm">超级 VIP 用户</Tag>可获取令牌
      </div>
      {userinfo.level === LEVEL_ENUM.SUPER_VIP && (
        <div className="mb-md" style={{ maxWidth: '500px' }}>
          <Input
            className="mb-md"
            addonBefore={'用户名'}
            value={userinfo.username}
            addonAfter={
              <CopyToClipboard
                text={userinfo.username}
                onCopy={() => message.success(`已复制令牌用户名：${userinfo.username}`)
                }
              >
                <Button size="small" type="text" shape="circle" icon={<Copy />} />
              </CopyToClipboard>
            }
          />
          {token && (
            <Input.Password
              addonBefore={'Token'}
              addonAfter={
                <>
                  <CopyToClipboard
                    text={token}
                    onCopy={() => message.success(`已复制令牌：${token}`)}
                  >
                    <Button
                      size="small"
                      type="text"
                      shape="circle"
                      icon={<Copy />}
                    />
                  </CopyToClipboard>
                  <Divider type="vertical" />
                  <Tooltip title="刷新令牌">
                    <Button
                      onClick={onUpdateTokenHandle}
                      size="small"
                      type="text"
                      shape="circle"
                      icon={<Sync />}
                    />
                  </Tooltip>
                </>
              }
              value={token}
            />
          )}
        </div>
      )}
    </Content>
  );
};

export default Token;
