// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import '@src/common/style/index.scss';
import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, combineReducers } from 'redux';
import Cookie from 'universal-cookie';
import { ConfigProvider } from 'coding-oa-uikit';
import 'coding-oa-uikit/dist/coding-oa-uikit.css';

import { StoreProvider } from './context/store';
import reducers, { injectGlobalReducer } from './reducer';

import './i18n';
import Root from './root';

import pkg from '../package.json';

const ID = 'layout';
const cookie = new Cookie();
const language = cookie.get('language') || 'zh_CN';

let locale: any = '';
try {
  locale = require(`coding-oa-uikit/lib/locale/${language}.js`);
} catch (e) {
  locale = require('coding-oa-uikit/lib/locale/zh_CN.js');
}

const create = (rootDom: HTMLElement) => {
  const e = document.getElementById(ID);
  if (rootDom && !e) {
    const container = document.createElement('div');
    container.id = ID;
    rootDom.appendChild(container);
  }
};

function bootstrap() { console.log(''); }

const mount = (props: any) => {
  const { rootDom, injectAsyncReducer, store } = props;
  create(rootDom);
  injectAsyncReducer && injectGlobalReducer(injectAsyncReducer);
  render(
    <Provider store={store}>
      <StoreProvider>
        <ConfigProvider
          autoInsertSpaceInButton={false}
          locale={locale ? locale.default : undefined}
          getPopupContainer={node => (node ? node.parentNode : document.body)}
        >
          <Root />
        </ConfigProvider>
      </StoreProvider>
    </Provider>,
    document.getElementById(ID),
  );
};

const unmount = () => {
  const e = document.getElementById(ID);
  if (e) {
    unmountComponentAtNode(e);
  }
};

if (typeof window.microHook === 'object') {
  window.microHook.registerApp(pkg.name, {
    bootstrap,
    mount,
    unmount,
  });
} else {
  const store = createStore(combineReducers({ ...reducers }));
  mount({ store });
}
