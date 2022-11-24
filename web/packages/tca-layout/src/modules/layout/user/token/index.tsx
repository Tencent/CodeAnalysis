import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import CopyToClipboard from 'react-copy-to-clipboard';
import { Layout, Row, Col, Input, Button, message, notification, Divider, Tag, Popconfirm } from 'coding-oa-uikit';
import Copy from 'coding-oa-uikit/lib/icon/Copy';
import Sync from 'coding-oa-uikit/lib/icon/Sync';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';

// 项目内
import { UserState, NAMESPACE } from '@src/store/user';
import { LevelEnum } from '@src/constant';
import { userTokenAPI } from '@src/services/user';
import { getApiDocURL } from '@plat/util';

// 模块内
import s from '../style.scss';

const { Content } = Layout;

const { get: getUserToken, put: putUserToken } = userTokenAPI();

const UPDATE_TOKEN_NOTIFICATION = (
  <>
    <p>注意：需要更新相关配置，并重启服务。</p>
    <p className={s.confirmNote}>
      可能需要更新Token的位置包括：
      <br />
      - 客户端codedog.ini配置
      <br/>
      - 客户端config.ini配置
      <br/>
      - 客户端节点命令行启动参数
      <br/>
      - 调用腾讯云代码分析API的请求头部参数
    </p>
  </>
);

const UPDATE_TOKEN_CONFIRMATION = (<>
  <p>确认要刷新个人令牌吗？</p>
  <p className={s.confirmNote}>刷新后，所有用到token的地方都需要更新，请谨慎操作！</p>
</>);

const Token = () => {
  const [token, setToken] = useState('');
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const { level, username } = userinfo;
  const { t } = useTranslation();

  useEffect(() => {
    if (level === LevelEnum.SUPER_VIP) {
      getUserToken().then(({ token }: any) => {
        setToken(token);
      });
    }
  }, []);

  /** 刷新个人token */
  const onUpdateTokenHandler = () => {
    putUserToken(null).then(({ token }: any) => {
      notification.success({
        key: 'update_token',
        message: 'Token已刷新',
        description: UPDATE_TOKEN_NOTIFICATION,
        duration: 10,
      });
      setToken(token);
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
        <a href={getApiDocURL()} target="_blank" rel="noreferrer">
          腾讯云代码分析 API
        </a> 和启动客户端分析
        ，仅<Tag className={s.userTag} color='volcano'>超级 VIP 用户</Tag>可获取令牌
      </div>
      {level === LevelEnum.SUPER_VIP && (
        <div className="mb-md" style={{ maxWidth: '500px' }}>
          <Input
            className="mb-md"
            addonBefore={'用户名'}
            value={username}
            addonAfter={
              <CopyToClipboard
                text={username}
                onCopy={() => {
                  message.success(`已复制令牌用户名：${username}`);
                }}
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
                    onCopy={() => {
                      message.success(`已复制令牌：${token}`);
                    }}
                  >
                    <Button
                      size="small"
                      type="text"
                      shape="circle"
                      icon={<Copy />}
                    />
                  </CopyToClipboard>
                  <Divider type="vertical" />
                  <Popconfirm
                    title={UPDATE_TOKEN_CONFIRMATION}
                    onConfirm={() => onUpdateTokenHandler()}
                    okText="确认"
                    getPopupContainer={() => document.body}
                  >
                    <Button
                      size="small"
                      type="text"
                      shape="circle"
                      icon={<Sync />}
                    />
                  </Popconfirm>
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
