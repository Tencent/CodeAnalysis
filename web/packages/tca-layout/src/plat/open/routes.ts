import { lazy } from 'react';
import { RouteProps } from 'react-router-dom';
import 'tdesign-react/es/style/index.css';

// 项目内
import Teams from '@src/modules/team';
import Invite from '@src/modules/team/components/invite';

const Manage = lazy(() => import('@src/modules/layout/manage'));
const User = lazy(() => import('@src/modules/layout/user'));
const Team = lazy(() => import('@src/modules/layout/team'));
const GitOAuth = lazy(() => import('@src/modules/layout/user/auth/git-oauth'));


const ROUTERS: RouteProps[] = [{
  path: '/teams',
  component: Teams,
}, {
  path: '/manage',
  component: Manage,
}, {
  path: '/user',
  component: User,
}, {
  path: '/t/invite/:code',
  component: Invite,
}, {
  path: '/t/:orgSid',
  component: Team,
}, {
  path: '/cb_git_auth/:scmPlatformName',
  component: GitOAuth,
}];

export default ROUTERS;
