/**
 * 挂载数据到window上
 */
import { Store } from 'redux';

import { registration } from '@src/register';
import { InjectAsyncReducer } from '@src/store';

const HOOK_NAME = 'microHook';
const DEV_API_LIST_NAME = 'microDevApiList';

export default (store: Store, injectAsyncReducer: InjectAsyncReducer) => {
  /**
   * 挂载 window 注册函数，禁止复写
   */
  if (!window.hasOwnProperty.call(window, HOOK_NAME)) {
    const hook: WindowMicroHook = {
      registerApp: registration.register,
      meta: [],
      store,
      injectAsyncReducer,
    };

    Object.defineProperty(window, HOOK_NAME, {
      enumerable: false,
      writable: false,
      value: hook,
    });
  }

  if (!window.hasOwnProperty.call(window, DEV_API_LIST_NAME)) {
    const apiList: MicroDevApiList[] = [];
    Object.defineProperty(window, DEV_API_LIST_NAME, {
      enumerable: false,
      writable: false,
      value: apiList,
    });
  }
};
