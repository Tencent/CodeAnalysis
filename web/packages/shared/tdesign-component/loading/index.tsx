/**
 * 加载中组件
 */

import React from 'react';
import { Loading as TLoading, LoadingProps } from 'tdesign-react';

const Loading = ({ loading = true, text = '加载中', size = 'small' }: LoadingProps) => <div className='tca-text-center tca-pa-md'>
  <TLoading loading={loading} text={text} size={size} />
</div>;

export default Loading;
