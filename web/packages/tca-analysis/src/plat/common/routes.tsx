import React, { lazy } from 'react';
import { RouteProps } from 'react-router-dom';

// 项目内
import { RouteListener as BaseRouteListener } from '@tencent/micro-frontend-shared/component/route';
import { BASE_ROUTE_PREFIX, TMPL_ROUTE_PREFIX } from '@src/constant';

const Repo = lazy(() => import('@src/modules/repos/repo'));
const Repos = lazy(() => import('@src/modules/repos'));
const PTOverview = lazy(() => import('@src/modules/project-team/overview'));
const PTGroup = lazy(() => import('@src/modules/project-team/group'));
const AllRules = lazy(() => import('@src/modules/template/code-lint/all-rules'));
const PkgRules = lazy(() => import('@src/modules/template/code-lint/pkg-rules'));
const CheckRules = lazy(() => import('@src/modules/template/code-lint/rules'));
const TemplateDetail = lazy(() => import('@src/modules/template/detail'));
const Template = lazy(() => import('@src/modules/template'));
// const PkgRules = lazy(() => import('@src/modules/template/code-lint/pkg-rules'));


const ROUTERS: RouteProps[] = [{
  path: `${BASE_ROUTE_PREFIX}/repos/:repoId`,
  exact: true,
  component: Repo,
}, {
  path: `${BASE_ROUTE_PREFIX}/repos`,
  exact: true,
  component: Repos,
}, {
  path: `${BASE_ROUTE_PREFIX}/profile`,
  exact: true,
  component: PTOverview,
}, {
  path: `${BASE_ROUTE_PREFIX}/group`,
  exact: true,
  component: PTGroup,
}, {
  path: `${TMPL_ROUTE_PREFIX}/:id/check-profiles/:checkProfileId/pkg/:pkgId/add-rule`,
  exact: true,
  component: AllRules,
}, {
  path: `${TMPL_ROUTE_PREFIX}/:id/check-profiles/:checkProfileId/checkrules`,
  exact: true,
  component: CheckRules,
}, {
  path: `${TMPL_ROUTE_PREFIX}/:id/check-profiles/:checkProfileId/pkg/:pkgId`,
  exact: true,
  component: PkgRules,
}, {
  path: `${TMPL_ROUTE_PREFIX}/:id/:tabs?`,
  component: TemplateDetail,
}, {
  path: TMPL_ROUTE_PREFIX,
  component: Template,
}];

export default ROUTERS;

interface RouteListenerProps {
  children: React.ReactNode;
}

export const RouteListener = ({ children }: RouteListenerProps) => <BaseRouteListener >{children}</BaseRouteListener>;

/** 格式化 a _blank 的 href，默认不做处理 */
export const formatBlankHref = (href: string) => href;
