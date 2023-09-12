import React from 'react';
import { Form, FormRule } from 'tdesign-react';

import TagSelect, { TagSelectProps } from './select';

interface NodeTagProps extends TagSelectProps {
  /** Form.Item name */
  name: string;
  /** Form.Item label */
  label: string | React.ReactNode
  /** Form.Item 校验规则 */
  rules?: FormRule[];
}

const { FormItem } = Form;

/** 运行环境表单项 */
const NodeTag = ({
  label, name, rules, ...other
}: NodeTagProps) => <FormItem label={label} name={name} rules={rules}>
    <TagSelect {...other} />
  </FormItem>;

NodeTag.Select = TagSelect;

export default NodeTag;
