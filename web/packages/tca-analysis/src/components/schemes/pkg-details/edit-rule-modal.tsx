// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 编辑规则弹框
 */

import React, { useEffect } from 'react';
import { toNumber, get } from 'lodash';
import { Dialog, Form, Radio, Textarea } from 'tdesign-react';

import { SEVERITY } from '@src/constant';

const { FormItem } = Form;

interface EditRuleModalProps {
  visible: boolean;
  data: any;
  onCancel: () => void;
  onEditRule: (updateData: any) => void;
}

const EditRuleModal = (props: EditRuleModalProps) => {
  const [form] = Form.useForm();
  const { data, visible, onCancel, onEditRule } = props;

  useEffect(() => {
    if (visible) {
      form.setFieldsValue(data);
    } else {
      form.reset();
    }
  }, [visible, form, data]);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validate().then((result: any) => {
      if (result === true) {
        const formData = form.getFieldsValue(true);
        const updateRule = {
          packagemaps: [data.id],
          rule_params: formData.rule_params === get(data, 'checkrule.rule_params') ? null : formData.rule_params,
          severity: formData.severity,
          state: data.state,
        };
        onEditRule(updateRule);
      }
    });
  };

  return (
    <Dialog
      header="编辑规则信息"
      visible={visible}
      onClose={onCancel}
      width={460}
      onConfirm={onSubmitHandle}
    >
      <Form
        layout='vertical'
        form={form}
        initialData={{ ...data, rule_params: data.rule_params || get(data, 'checkrule.rule_params') }}
      >
        <FormItem
          label='规则严重级别'
          name='severity'
        >
          <Radio.Group>
            {
              Object.keys(SEVERITY).map((key: any) => (
                <Radio value={toNumber(key)} key={toNumber(key)}>{SEVERITY[key]}</Radio>
              ))
            }
          </Radio.Group>
        </FormItem>
        <FormItem
          label='规则参数'
          name='rule_params'
          style={{ marginBottom: 0 }}
        >
          <Textarea placeholder='请输入规则参数' />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default EditRuleModal;
