// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

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
  name: string; url: string
}

interface Window {
  microHook: WindowMicroHook;
  microDevApiList: Array<MicroDevApiList>;
}
