// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// global typescript
declare module '*.scss';
declare module '*.svg';

type Store = import('redux').Store;
type Reducer = import('redux').Reducer;

// LifeCycle
interface LifeCycle<T = {}> {
  bootstrap: (config: T) => void;
  mount: (config: T) => void;
  unmount: (config: T) => void;
  update?: (config: T) => void;
}

// RegisterMicroApp
type RegisterMicroApp = (id: string, lifecycle: LifeCycle) => void;

// TInjectAsyncReducer
type TInjectAsyncReducer = (name: string, reducer: Reducer, override?: boolean) => void;

// MicroApplicationProps
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

// MicroApplication
interface MicroApplication {
  props: MicroApplicationProps;
  readonly loadStyle: () => Promise<any>;
  readonly loadScript: () => Promise<any>;
  readonly loadResources: () => Promise<any>;
  readonly removeStyle: () => Promise<any>;
  readonly path: () => RegExp;
}

// WindowMicroHook
interface WindowMicroHook {
  registerApp: RegisterMicroApp;
  injectAsyncReducer: TInjectAsyncReducer;
  store: Store;
  meta: MicroApplication[];
}

interface Window {
  microHook: WindowMicroHook;
}

declare const PLATFORM_ENV: 'saas' | 'private' | 'oa';

declare const ENABLE_MANAGE: 'TRUE';
