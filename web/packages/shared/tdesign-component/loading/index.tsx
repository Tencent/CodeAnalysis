/**
 * 加载中组件
 */

import React from 'react';
import { LoadingIcon } from 'tdesign-icons-react';
import s from './style.scss';

const Loading = () => <div className={s.loading}>
  <LoadingIcon className={s.icon} />
  加载中
</div>;

export default Loading;
