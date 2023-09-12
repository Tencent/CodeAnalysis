declare module '*.scss';

type Store = import('redux').Store;
type LifeCycle = import('@src/register').LifeCycle;
type RegisterMicroApp = (id: string, lifecycle: LifeCycle) => void;

interface WindowMicroHook {
  registerApp: RegisterMicroApp;
  injectAsyncReducer: import('@src/store').TInjectAsyncReducer;
  store: Store;
  meta: import('@src/meta/application').default[];
}

interface MicroDevApiList {
  name: string;
  url: string;
  enabled?: boolean;
}

interface Window {
  microHook: WindowMicroHook;
  microDevApiList: Array<MicroDevApiList>;
}
