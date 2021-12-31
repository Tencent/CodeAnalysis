import GLOBAL_BREADCRUMB from '@src/components/global-breadcrumb/reducer';
import INITIAL from './initial';
import APP from './app';

const reducers = {
  APP,
  INITIAL,
  GLOBAL_BREADCRUMB,
};

export const injectGlobalReducer = (injectAsyncReducer: TInjectAsyncReducer) => {
  Object.keys(reducers).forEach((key: 'APP' | 'INITIAL' | 'GLOBAL_BREADCRUMB') => injectAsyncReducer(key, reducers[key]));
};

export default reducers
