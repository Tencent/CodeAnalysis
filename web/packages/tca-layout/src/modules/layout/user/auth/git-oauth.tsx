import React from 'react';

// 项目内
import BaseGitOAuthCallack from '@tencent/micro-frontend-shared/tca/user-auth/git-oauth';
import { userAuthAPI } from '@plat/api';
import Container from '@src/component/container';

/** git oauth 回调 */
const GitOAuthCallack = () => <Container><BaseGitOAuthCallack oauthCallback={userAuthAPI.oauthCallback} /></Container>;

export default GitOAuthCallack;
