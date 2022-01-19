// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

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
