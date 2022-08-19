/**
 * 过滤筛选组件
 */

import React from 'react';
import Form, { FormProps } from 'coding-oa-uikit/lib/form';

import Item from './FilterItem';

const Filter = (props: FormProps) => {
  const { children, layout = 'inline', ...formProps } = props;
  return (
    <Form
      {...formProps}
      layout={layout}
    >
      {children}
    </Form>
  );
};

Filter.Item = Item;

export default Filter;
