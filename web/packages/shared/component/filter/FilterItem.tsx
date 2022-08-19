import React from 'react';
import Form, { FormItemProps } from 'coding-oa-uikit/lib/form';

const Item = (props: FormItemProps) => {
  const { children, ...formItemProps } = props;
  return (
    <Form.Item
      htmlFor=''  // 避免 label 触发事件
      {...formItemProps}
    >
      {children}
    </Form.Item>
  );
};

export default Item;
