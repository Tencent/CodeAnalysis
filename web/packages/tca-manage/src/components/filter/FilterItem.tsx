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
      label={label ? `${label}：` : null}
      {...otherProps}
    >
      {children}
    </Form.Item>
  );
};

export default Item;
