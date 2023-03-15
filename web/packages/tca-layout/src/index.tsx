import React from 'react';
import MicroInit from '@tencent/micro-frontend-shared/component/micro-init';

// 项目内
import './style.scss';
import Root from './root';
import stores from './store';
import { State, Action } from './store/types';
import reducers from './reducer';
import pkg from '../package.json';

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
