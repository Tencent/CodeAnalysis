import React from 'react';
import MicroInit from '@tencent/micro-frontend-shared/tdesign-component/micro-init';
import MicroLayout from '@tencent/micro-frontend-shared/tdesign-component/micro-layout';

// 项目内
import Root from './root';
import pkg from '../package.json';

MicroInit({
  id: 'container',
  name: pkg.name,
  container:
    <MicroLayout value="completed" loading={null}>
      <Root />
    </MicroLayout>,
});
