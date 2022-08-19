/**
 * 加载中组件
 */

import React from 'react';
import LoadingIcon from 'coding-oa-uikit/lib/icon/Loading';
import s from './style.scss';

interface LoadingProps {
  msg?: string;
}

const Loading = ({ msg = '加载中' }: LoadingProps) => <div className={s.loading}>
  <LoadingIcon className={s.icon} />
  {msg}
</div>;

export default Loading;
