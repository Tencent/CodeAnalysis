import React from 'react';
import MicroInit from '@tencent/micro-frontend-shared/component/micro-init';
import MicroLayout from '@tencent/micro-frontend-shared/component/micro-layout';
import initI18next from '@tencent/micro-frontend-shared/i18n';
import { isTrue } from '@tencent/micro-frontend-shared/util';
import { initReactI18next } from 'react-i18next';
// import { StoreProvider } from './context/store';

// 项目内
import Root from './root';
import stores from './store';
import { State, Action } from './store/types';
import pkg from '../package.json';

// 初始化i18n
initI18next({ modules: [initReactI18next] });

MicroInit<State, Action>({
  id: 'container',
  name: pkg.name,
  container: (
    <MicroLayout value="projectCompleted" disable={isTrue(process.env.DISABLE_MICRO_LAYOUT)}>
      <Root />
    </MicroLayout>
  ),
  hookStore: {
    enable: true,
    stores,
  },
});
