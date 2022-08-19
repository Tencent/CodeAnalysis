import { RouteProps } from 'react-router-dom';

// 项目内
import Login from '@src/modules';

const ROUTERS: RouteProps[] = [{
  path: '/login',
  exact: true,
  component: Login,
}];

export default ROUTERS;
