// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import cn from 'classnames';
import { Form } from 'tdesign-react';
import s from './style.scss';

const { FormItem } = Form;

interface ItemProps {
  children: React.ReactNode;
  label?: string;
  className?: any;
}

const Item = (props: ItemProps & any) => {
  const { children, label, className, ...otherProps } = props;
  return (
        <FormItem
            className={cn(className, s.filterItem)}
            htmlFor=''  // 避免 label 触发事件
            label={label ? `${label}：` : null}
            {...otherProps}
        >
            {children}
        </FormItem>
  );
};

export default Item;
