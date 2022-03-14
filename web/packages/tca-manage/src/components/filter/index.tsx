/**
 * 过滤筛选组件
 */

import React from 'react';
import { Form } from 'coding-oa-uikit';

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
    >
      {children}
    </Form>
  );
};

Filter.Item = Item;

export default Filter;
