/**
 * 加载中组件
 */

import React from 'react';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';

import style from './style.scss';

const Loading = () => (
  <div className={style.loading}>
    <LoadingIcon className={style.icon} />
    加载中
  </div>
);

export default Loading;
