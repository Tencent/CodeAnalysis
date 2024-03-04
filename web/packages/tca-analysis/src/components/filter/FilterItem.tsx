// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import cn from 'classnames';
import { Form } from 'coding-oa-uikit';

interface ItemProps {
  children: React.ReactNode;
  label?: string;
  className?: any;
}

const Item = (props: ItemProps & any) => {
  const { children, label, className, ...otherProps } = props;
  return (
    <Form.Item
      className={cn(className)}
      htmlFor=''  // 避免 label 触发事件
      label={label ? `${label}：` : null}
      {...otherProps}
    >
      {children}
    </Form.Item>
  );
};

export default Item;
