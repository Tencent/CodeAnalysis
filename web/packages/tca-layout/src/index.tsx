import React from 'react';
import MicroInit from '@tencent/micro-frontend-shared/component/micro-init';
import initI18next from '@tencent/micro-frontend-shared/i18n';
import { initReactI18next } from 'react-i18next';

// 项目内
import './style.scss';
import Root from './root';
import stores from './store';
import { State, Action } from './store/types';
import reducers from './reducer';
import pkg from '../package.json';

// 初始化i18n
initI18next({ modules: [initReactI18next] });

MicroInit<State, Action>({
  id: 'layout',
  name: pkg.name,
  container: <Root />,
  reducers,
  hookStore: {
    enable: true,
    stores,
  },
});
