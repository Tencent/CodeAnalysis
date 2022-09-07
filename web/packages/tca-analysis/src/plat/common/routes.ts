import { lazy } from 'react';
import { RouteProps } from 'react-router-dom';

// 项目内
import { BASE_ROUTE_PREFIX, TMPL_ROUTE_PREFIX } from '@src/constant';

const PTOverview = lazy(() => import('@src/modules/project-team/overview'));
const PTGroup = lazy(() => import('@src/modules/project-team/group'));
const AllRules = lazy(() => import('@src/modules/template/code-lint/all-rules'));
const PkgRules = lazy(() => import('@src/modules/template/code-lint/pkg-rules'));
const TemplateDetail = lazy(() => import('@src/modules/template/detail'));
const Template = lazy(() => import('@src/modules/template'));
// const PkgRules = lazy(() => import('@src/modules/template/code-lint/pkg-rules'));


const ROUTERS: RouteProps[] = [{
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

