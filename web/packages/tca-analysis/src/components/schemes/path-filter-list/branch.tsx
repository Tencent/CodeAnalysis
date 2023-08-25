// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect } from 'react';

import { Switch, Form, Input, Button, SubmitContext } from 'tdesign-react';
import FormLabelWithHelp from '@src/components/title-with-help';

const { FormItem } = Form;

interface IProps {
  data: any;
  isSysTmpl?: boolean;
  updateData: (field: string, value: any) => void;
}

const Branch = (props: IProps) => {
  const { updateData, isSysTmpl = false, data } = props;
  const [form] = Form.useForm();
  const ignoreMergedIssue = Form.useWatch('ignore_merged_issue', form);

  useEffect(() => {
    if (data.id) {
      form.reset();
    }
  }, [form, data.id]);


  const onFinish = (context: SubmitContext<FormData>) => {
    if (context.validateResult === true) {
      const formData = form.getFieldsValue(true);
      updateData('ignore_branch_issue', formData.ignore_branch_issue);
    }
  };

  return (
    <Form
      labelAlign="left"
      style={{ width: 640 }}
      labelWidth={240}
      initialData={data}
      resetType='initial'
      form={form}
      onSubmit={onFinish}
    >
      <FormItem
        label={<FormLabelWithHelp labelString='过滤其他分支合入问题' helpInfo='常用于合流场景分支分析，过滤掉从其他分支同步代码引入的问题'/>}
        name='ignore_merged_issue'
      >
        <Switch
          size='small'
          onChange={(checked: any) => updateData('ignore_merged_issue', checked)}
          disabled={isSysTmpl}
        />
      </FormItem>
      {ignoreMergedIssue && (
        <FormItem
          name="ignore_branch_issue"
          label={<FormLabelWithHelp labelString='对比分支' helpInfo='只针对Git生效需要过滤父分支问题时使用，常用于合流场景，分析子分支时，过滤掉从父分支引入的历史代码问题'/>}
        >
          <Input placeholder="请输入分支名称" />
        </FormItem>
      )}
      <FormItem
        label={<FormLabelWithHelp
          labelString='全局代码检查Issue忽略状态同步'
          helpInfo='默认为关闭状态。开启则表示如果代码库内存在相同Issue且为忽略状态，则利用该分析方案发现该Issue时会同步忽略该Issue；关闭则表示不受全局代码检查Issue影响'
        />}
        name='issue_global_ignore'
      >
        <Switch
          size='small'
          disabled={isSysTmpl}
          onChange={checked => updateData('issue_global_ignore', checked)}
        />
      </FormItem>
      {!isSysTmpl && <FormItem style={{ marginTop: 30 }}>
        <Button theme='primary' type='submit' style={{ marginRight: 10 }}>保存</Button>
        <Button theme='default' type='reset'>取消</Button>
      </FormItem>}
    </Form>
  );
};

export default Branch;
