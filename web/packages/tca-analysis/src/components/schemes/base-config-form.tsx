// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 基础属性
 */

import React from 'react';
import { get } from 'lodash';

import {
  Form,
  Input,
  Select,
  Textarea,
} from 'tdesign-react';

import NodeTag from '@src/components/node-tag';

const { FormItem } = Form;

interface BaseConfigFormProps {
  name: '方案' | '模板';
  readonly?: boolean;
  tags: any[];
  languages: any[];
  data: any;
}

const BaseConfigForm = ({
  name,
  tags,
  languages,
  data,
  readonly = false,
}: BaseConfigFormProps) => (<>
  <FormItem
    name="name"
    label={`${name}名称`}
    rules={[
      { required: true, message: `请输入${name}名称` },
      { max: 127, message: `${name}名称过长` },
    ]}
  >
    <Input readonly={readonly} placeholder={`请输入${name}名称`} />
  </FormItem>
  <FormItem name="description" label={`${name}描述`} initialData={get(data, 'description', '')}>
    <Textarea readonly={readonly} rows={3} placeholder={`请输入${name}描述`} />
  </FormItem>
  <FormItem
    name="languages"
    label="分析语言"
    rules={[{ required: true, message: '请选择分析语言' }]}
  >
    <Select
      multiple
      placeholder="请选择分析语言"
      filterable
      options={languages}
      readonly={readonly}
      keys={{
        label: 'display_name',
        value: 'name',
      }}
    />
  </FormItem>
  <NodeTag
    name="tag"
    label="运行环境"
    rules={[{ required: true, message: '请选择运行环境' }]}
    tags={tags}
    readonly={readonly}
  />
  <FormItem name="envs" label="环境变量">
    <Textarea rows={3} placeholder="请输入环境变量" readonly={readonly} />
  </FormItem>
</>);

export default BaseConfigForm;
