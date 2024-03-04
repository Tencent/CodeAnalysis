// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import cn from 'classnames';
import Runing from 'coding-oa-uikit/lib/icon/Runing';

import style from './style.scss';

interface RuningIconProps {
  className?: any
}

const RuningIcon = (props: RuningIconProps) => {
  const { className } = props;
  return (
        <Runing className={cn(style.running, className)}/>
  );
};

export default RuningIcon;

