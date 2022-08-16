declare module '*.scss';
type Store = import('redux').Store;
type Reducer = import('redux').Reducer;

interface LifeCycle<T> {
  bootstrap: (config: T) => void;
  mount: (config: T) => Promise<void> | void;
  unmount: (config: T) => void;
  update?: (config: T) => void;
}

type RegisterMicroApp = (id: string, lifecycle: LifeCycle<any>) => void;
interface InjectReducer {
  [key: string]: Reducer;
}

type InjectAsyncReducer = (name: string, reducer: Reducer, override?: boolean) => void;

interface ApplicationCustomProps {
  rootDom: HTMLElement;
  store: Store;
  injectAsyncReducer?: InjectAsyncReducer;
}

interface MicroApplicationProps {
  name: string;
  description: string;
  match: string;
  commitId?: string;
  changeAt?: string;
  css: string[];
  js: string[];
  prefix: string[] | string;
}

interface MicroApplication {
  props: MicroApplicationProps;
  readonly loadStyle: () => Promise<any>;
  readonly loadScript: () => Promise<any>;
  readonly loadResources: () => Promise<any>;
  readonly removeStyle: () => Promise<any>;
  readonly path: () => RegExp;
}

interface WindowMicroHook {
  registerApp: RegisterMicroApp;
  injectAsyncReducer: InjectAsyncReducer;
  store: Store;
  meta: MicroApplication[];
}

interface Window {
  microHook: WindowMicroHook;
}
