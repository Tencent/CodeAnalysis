// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import classnames from 'classnames';

// 项目内
import { t } from '@src/i18n/i18next';
import Figure from '@src/images/figure.svg';
interface INoDataProps {
  className?: string;
  style?: React.CSSProperties;
}

const NoData = ({ className, style }: INoDataProps) => (
        <div className={classnames('text-center', className)} style={style}>
            <img src={Figure} alt={t('暂无数据')} />
            <p className="mt-sm text-grey-6 fs-12">{t('暂无数据')}</p>
        </div>
);

export default NoData;
