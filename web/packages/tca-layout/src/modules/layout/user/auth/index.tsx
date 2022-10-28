import React from 'react';
import { Layout } from 'coding-oa-uikit';

// 项目内
import UserAuth from '@tencent/micro-frontend-shared/tca/user-auth';
import { userAuthAPI } from '@plat/api';

const { Content } = Layout;


interface AuthProps {
  /** 展示凭证创建渠道，默认false */
  showOrigin?: boolean;
}

const Auth = ({ showOrigin }: AuthProps) => (
  <Content className="pa-lg">
    <UserAuth userAuthAPI={userAuthAPI} showOrigin={showOrigin} />
  </Content>
);

export default Auth;
