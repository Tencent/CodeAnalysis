import { createStore, combineReducers, Reducer } from 'redux';
import allowedReducers from './allowed-reducers';

interface InjectReducer {
  [key: string]: Reducer;
}
const ASYNC_REDUCERS: InjectReducer = {};

export type TInjectAsyncReducer = (name: string, reducer: Reducer, override?: boolean) => void;

function createGlobalStore() {
  // 将store挂载到window
  const rootReducers = {};
  const store = createStore(combineReducers({ ...rootReducers }));

  const injectAsyncReducer: TInjectAsyncReducer = (name: string, reducer: Reducer, override = false) => {
    // reducer白名单控制
    if (!allowedReducers.includes(name)) {
      throw new Error(`[injectAsyncReducer] not allowed inject reducer namespace ${name}`);
    }
    // 默认不允许覆盖
    if (ASYNC_REDUCERS[name] && !override) {
      return;
    }
    ASYNC_REDUCERS[name] = reducer;
    store.replaceReducer(combineReducers({ ...rootReducers, ...ASYNC_REDUCERS }));
  };
  return {
    store,
    injectAsyncReducer,
  };
}

const creator = createGlobalStore();
export const { store } = creator;
export const { injectAsyncReducer } = creator;
