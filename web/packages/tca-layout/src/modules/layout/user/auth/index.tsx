import React from 'react';

// 项目内
import UserAuth from '@tencent/micro-frontend-shared/tca/user-auth';
import { userAuthAPI } from '@plat/api';


interface AuthProps {
  /** 展示凭证创建渠道，默认false */
  showOrigin?: boolean;
}

const Auth = ({ showOrigin }: AuthProps) => (
  <UserAuth userAuthAPI={userAuthAPI} showOrigin={showOrigin} />
);

export default Auth;
