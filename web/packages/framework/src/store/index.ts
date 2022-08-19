import { createStore, combineReducers, Reducer } from 'redux';
import allowedReducers from './allowed-reducers';

interface InjectReducer {
  [key: string]: Reducer;
}
const ASYNC_REDUCERS: InjectReducer = {};

export type InjectAsyncReducer = (name: string, reducer: Reducer, override?: boolean) => void;

/**
 * 创建全局store
 * @returns store, injectAsyncReducer
 */
const createGlobalStore = () => {
  /** 设置 root reducers */
  const rootReducers: InjectReducer = {};
  const store = createStore(combineReducers({ ...rootReducers }));

  /**
   * 注入reducer
   * @param name 名称
   * @param reducer reducer
   * @param override 是否覆盖，默认不覆盖
   * @returns
   */
  const injectAsyncReducer: InjectAsyncReducer = (name: string, reducer: Reducer, override = false) => {
    // reducer白名单控制
    if (!allowedReducers.includes(name)) {
      throw new Error(`[injectAsyncReducer] not allowed inject reducer namespace ${name}`);
    }
    // 默认不允许覆盖
    if (!(ASYNC_REDUCERS[name] && !override)) {
      ASYNC_REDUCERS[name] = reducer;
      store.replaceReducer(combineReducers({ ...rootReducers, ...ASYNC_REDUCERS }));
    }
  };

  return {
    store,
    injectAsyncReducer,
  };
};

const creator = createGlobalStore();
export const { store } = creator;
export const { injectAsyncReducer } = creator;
