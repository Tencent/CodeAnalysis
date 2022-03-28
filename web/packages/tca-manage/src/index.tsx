import './i18n';
import './index.scss';
import 'coding-oa-uikit/dist/coding-oa-uikit.css';
import pkg from '../package.json';


import React from 'react';
import { render, unmountComponentAtNode } from 'react-dom';
import { Provider } from 'react-redux';
import { createStore, combineReducers } from 'redux';
import { ConfigProvider } from 'coding-oa-uikit';
import Cookie from 'universal-cookie';
import { StoreProvider } from './context/store';
import MicroLayout from './micro-layout';

import Root from './root';

const ID = 'container';
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

function bootstrap() { }

const mount = (props: any) => {
  const { rootDom, store } = props;
  create(rootDom);
  render(
    <Provider store={store}>
      <StoreProvider>
        <ConfigProvider
          autoInsertSpaceInButton={false}
          locale={locale ? locale.default : undefined}
          // @ts-ignore
          getPopupContainer={node => (node ? node.parentNode : document.body)}
        >
          <MicroLayout value="completed">
            <Root />
          </MicroLayout>
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
  const store = createStore(combineReducers({}));
  mount({ store });
}
