// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 加载中组件
 */

import React from 'react';
import { Loading, LoadingProps } from 'tdesign-react';

import style from './style.scss';

const SingleLoading = (props: LoadingProps) => (
        <div className={style.loading}>
            <Loading {...props} />
        </div>
);

export default SingleLoading;
