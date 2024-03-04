// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 提示组件
 */

import React from 'react';
import cn from 'classnames';
import { Tooltip } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';

import style from './style.scss';

interface TipsProps {
  title: string | React.ReactNode;
  className?: any;
  icon?: React.ReactNode
}

const Tips = (props: TipsProps) => {
  const { title, className, icon, ...otherProps } = props;

  return (
    <Tooltip
      title={title}
      {...otherProps}
    >
      <span>
        {
          icon ? (
            icon
          ) : (
            <QuestionCircle className={cn(style.questionIcon, className)} />
          )
        }
      </span>
    </Tooltip>
  );
};

export default Tips;
