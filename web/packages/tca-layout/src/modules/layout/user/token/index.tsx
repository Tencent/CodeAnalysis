import React, { useEffect, useState } from 'react';
import CopyToClipboard from 'react-copy-to-clipboard';
import { Layout, Input, InputAdornment, Button, Popconfirm, Space, message, NotificationPlugin } from 'tdesign-react';
import { FileCopyIcon, RefreshIcon } from 'tdesign-icons-react';

import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

// 项目内
import { getApiDocURL } from '@plat/util';

import { UserState, NAMESPACE } from '@src/store/user';
import { LevelEnum } from '@src/constant';
import { userTokenAPI } from '@src/services/user';

// 模块内

const { get: getUserToken, put: putUserToken } = userTokenAPI();

const UPDATE_TOKEN_NOTIFICATION = (
  <>
    <p>注意：需要更新相关配置，并重启服务。</p>
    <p className='tca-fs-12' style={{ color: 'var(--tca-text-color-secondary)' }}>
      可能需要更新Token的位置包括：
      <br />
      - 客户端codedog.ini配置
      <br />
      - 客户端config.ini配置
      <br />
      - 客户端节点命令行启动参数
      <br />
      - 调用腾讯云代码分析API的请求头部参数
    </p>
  </>
);

const UPDATE_TOKEN_CONFIRMATION = (<>
  <p>确认要刷新个人令牌吗？</p>
  <p className='tca-fs-12' style={{ color: 'var(--tca-text-color-secondary)' }}>刷新后，所有用到token的地方都需要更新，请谨慎操作！</p>
</>);

const Token = () => {
  const [token, setToken] = useState('');
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const { level, username } = userinfo;

  useEffect(() => {
    if (level === LevelEnum.SUPER_VIP) {
      getUserToken().then(({ token }: any) => {
        setToken(token);
      });
    }
  }, [level]);

  /** 刷新个人token */
  const onUpdateTokenHandler = () => {
    putUserToken(null).then(({ token }: any) => {
      NotificationPlugin.error({
        title: 'Token 已刷新',
        content: UPDATE_TOKEN_NOTIFICATION,
        duration: 10000,
        offset: [-24, 24],
        closeBtn: true,
      });
      setToken(token);
    });
  };

  return (
    <>
      <PageHeader title="个人令牌" description={<>
        个人访问令牌可用于访问 <a href={getApiDocURL()} target="_blank" rel="noreferrer">腾讯云代码分析 API</a>{' '}
        和启动客户端分析，仅<span style={{ color: 'var(--tca-warning-color)' }}>超级 VIP 用户</span>可获取令牌
      </>} />
      <Layout.Content className='tca-pa-lg'>
        <div style={{ width: 500 }}>
          {level === LevelEnum.SUPER_VIP && <>
            <InputAdornment className="tca-mb-md" prepend="用户名" append={<CopyToClipboard
              text={username}
              onCopy={() => {
                message.success(`已复制令牌用户名：${username}`);
              }}
            >
              <Button variant='text' shape="circle" icon={<FileCopyIcon />} />
            </CopyToClipboard>}>
              <Input value={username} />
            </InputAdornment>
            {token && <InputAdornment prepend="Token" append={<Space size={4}>
              <CopyToClipboard
                text={token}
                onCopy={() => {
                  message.success(`已复制令牌：${token}`);
                }}
              >
                <Button variant='text' shape="circle" icon={<FileCopyIcon />} />
              </CopyToClipboard>
              <Popconfirm
                theme='danger'
                content={UPDATE_TOKEN_CONFIRMATION}
                onConfirm={onUpdateTokenHandler}
              >
                <Button variant='text' shape="circle" icon={<RefreshIcon />} />
              </Popconfirm>
            </Space>}>
              <Input type="password" value={token} />
            </InputAdornment>}
          </>}
        </div>
      </Layout.Content>
    </>
  );
};

export default Token;
