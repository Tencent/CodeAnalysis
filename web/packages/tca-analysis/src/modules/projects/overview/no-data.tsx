// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import classnames from 'classnames';
import { useTranslation } from 'react-i18next';

// 项目内
import Figure from '@src/images/figure.svg';
interface INoDataProps {
  className?: string;
  style?: React.CSSProperties;
}

const NoData = ({ className, style }: INoDataProps) => {
  const { t } = useTranslation();

  return (
    <div className={classnames('text-center', className)} style={style}>
      <img src={Figure} alt={t('暂无数据')} />
      <p className="mt-sm text-grey-6 fs-12">{t('暂无数据')}</p>
    </div>
  );
};

export default NoData;
