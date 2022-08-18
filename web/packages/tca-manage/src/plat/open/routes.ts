import { lazy } from 'react';
import { RouteProps } from 'react-router-dom';

// 项目内
const Users = lazy(() => import('@src/modules/users'));
const Orgs = lazy(() => import('./modules/orgs'));
const Teams = lazy(() => import('./modules/teams'));
const Jobs = lazy(() => import('@src/modules/jobs'));
const Tools = lazy(() => import('@src/modules/tools'));
const Nodes = lazy(() => import('./modules/nodes'));
const NodeProcess = lazy(() => import('@src/modules/process'));
const OAuth = lazy(() => import('@src/modules/oauth'));

const ROUTERS: RouteProps[] = [{
  path: '/manage/users',
  component: Users,
}, {
  path: '/manage/orgs',
  component: Orgs,
}, {
  path: '/manage/teams',
  component: Teams,
}, {
  path: '/manage/jobs',
  component: Jobs,
}, {
  path: '/manage/tools',
  component: Tools,
}, {
  path: '/manage/nodes/:nodeId/process',
  component: NodeProcess,
}, {
  path: '/manage/nodes',
  component: Nodes,
}, {
  path: '/manage/oauths',
  component: OAuth,
}];

export default ROUTERS;
