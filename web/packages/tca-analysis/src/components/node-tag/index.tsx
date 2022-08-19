import React from 'react';
import { Form } from 'coding-oa-uikit';
import { ColProps } from 'coding-oa-uikit/lib/grid';
import { Rule } from 'coding-oa-uikit/lib/form';

import TagSelect, { TagSelectProps } from './select';

interface NodeTagProps extends TagSelectProps {
  /** Form.Item name */
  name: string;
  /** Form.Item label */
  label: string | React.ReactNode
  /** Form.Item 布局样式 */
  labelCol?: ColProps;
  /** Form.Item 布局样式 */
  wrapperCol?: ColProps;
  /** Form.Item 校验规则 */
  rules?: Rule[];
}

/** 运行环境表单项 */
const NodeTag = ({
  label, name, labelCol, wrapperCol, rules, ...other
}: NodeTagProps) => <Form.Item labelCol={labelCol} wrapperCol={wrapperCol} label={label} name={name} rules={rules}>
    <TagSelect {...other} />
  </Form.Item>;

NodeTag.Select = TagSelect;

export default NodeTag;
