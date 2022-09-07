import breadcrumbReducer from '@src/component/global-breadcrumb/reducer';
import initReducer from './initial';
import appReducer from './app';

const reducers = {
  APP: appReducer,
  INITIAL: initReducer,
  GLOBAL_BREADCRUMB: breadcrumbReducer,
};

export default reducers;
