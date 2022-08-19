import React from 'react';
import MicroInit from '@tencent/micro-frontend-shared/tdesign-component/micro-init';
import initI18next from '@tencent/micro-frontend-shared/i18n';
import { initReactI18next } from 'react-i18next';

// 项目内
import Root from './root';
import pkg from '../package.json';

// 初始化i18n
initI18next({ modules: [initReactI18next] });

MicroInit({
  id: 'container',
  name: pkg.name,
  container: <Root />,
});
