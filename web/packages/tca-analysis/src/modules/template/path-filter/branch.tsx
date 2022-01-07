// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';

import { Tooltip, Switch, Form } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';

import formStyle from '../style.scss';

const layout = {
  labelCol: { span: 9 },
  wrapperCol: { span: 15 },
  colon: false,
};

interface IProps {
  isSysTmpl: boolean;
  data: any;
  updateData: (field: string, value: any) => void;
}

const Branch = (props: IProps) => {
  const { updateData, data, isSysTmpl } = props;
  const [form] = Form.useForm();

  useEffect(() => {
    form.resetFields();
  }, [data.id]);

  const onFinish = (formData: any) => {
    updateData('ignore_branch_issue', formData.ignore_branch_issue);
  };

  return (
    <Form
      labelAlign="left"
      className={formStyle.schemeFormVertical}
      style={{ width: 640 }}
      initialValues={data}
      form={form}
      onFinish={onFinish}
    >
      <Form.Item
        {...layout}
        label={
          <span>
            全局代码检查Issue忽略状态同步
            <Tooltip
              // @ts-ignore
              getPopupContainer={() => document.getElementById('container')}
              title='默认为关闭状态。开启则表示如果代码库内存在相同Issue且为忽略状态，则利用该分析方案发现该Issue时会同步忽略该Issue；关闭则表示不受全局代码检查Issue影响'
            >
              <QuestionCircle className={formStyle.questionIcon} />
            </Tooltip>
          </span>
        }
      >
        <Switch
          size='small'
          disabled={isSysTmpl}
          checked={data.issue_global_ignore}
          onChange={checked => updateData('issue_global_ignore', checked)}
        />
      </Form.Item>
    </Form>
  );
};

export default Branch;
