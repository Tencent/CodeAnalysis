import { RouteProps } from 'react-router-dom';

// 项目内
import Teams from '@src/modules/team';
import Invite from '@src/modules/team/components/invite';
import Manage from '@src/modules/layout/manage';
import User from '@src/modules/layout/user';
import Team from '@src/modules/layout/team';
import GitOAuth from '@src/modules/layout/user/auth/git-oauth';

/** 根路由 */
export const ROOT_ROUTERS: RouteProps[] = [{
  path: '/teams',
  component: Teams,
}, {
  path: '/user',
  component: User,
}, {
  path: '/invite/:code',
  component: Invite,
  exact: true,
}, {
  path: '/t/:orgSid',
  component: Team,
}, {
  path: '/cb_git_auth/:scmPlatformName',
  component: GitOAuth,
}, {
  path: '/manage',
  component: Manage,
}];
