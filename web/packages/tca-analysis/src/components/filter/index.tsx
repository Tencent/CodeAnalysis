// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 过滤筛选组件
 */

import React from 'react';
import { Form } from 'tdesign-react';

import Item from './FilterItem';

interface FilterProps {
  children: React.ReactNode
}

const Filter = (props: FilterProps & any) => {
  const { children, ...otherProps } = props;
  return (
        <Form
            {...otherProps}
            layout="inline"
            labelAlign='left'
            labelWidth='auto'
        >
            {children}
        </Form>
  );
};

Filter.Item = Item;

export default Filter;
