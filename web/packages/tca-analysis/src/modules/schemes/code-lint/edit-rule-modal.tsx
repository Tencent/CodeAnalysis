/**
 * 编辑规则弹框
 */

import React, { useEffect } from 'react';
import { toNumber, get } from 'lodash';
import { Modal, Form, Radio, Input, message } from 'coding-oa-uikit';

import { modifyRule } from '@src/services/schemes';
import { SEVERITY } from '../constants';

interface EditRuleModalProps {
  orgSid: string;
  teamName: string;
  repoId: number | string;
  schemeId: number | string;
  visible: boolean;
  data: any;
  onCancel: () => void;
  callback: () => void;
}

const EditRuleModal = (props: EditRuleModalProps) => {
  const [form] = Form.useForm();
  const { orgSid, teamName, repoId, schemeId, data, visible, onCancel, callback } = props;

  useEffect(() => {
    visible && form.resetFields();
  }, [visible]);

  const onFinish = (formData: any) => {
    modifyRule(orgSid, teamName, repoId, schemeId, {
      packagemaps: [data.id],
      rule_params:
                formData.rule_params === get(data, 'checkrule.rule_params')
                  ? null
                  : formData.rule_params,
      severity: formData.severity,
      state: data.state,
    }).then(() => {
      message.success('修改规则成功');
      callback();
      onCancel();
    });
  };

  return (
        <Modal
            title="编辑规则信息"
            visible={visible}
            onCancel={onCancel}
            width={460}
            onOk={() => form.validateFields().then(onFinish)}
        >
            <Form
                layout="vertical"
                form={form}
                onFinish={onFinish}
                initialValues={{
                  ...data,
                  rule_params: data.rule_params || get(data, 'checkrule.rule_params'),
                }}
            >
                <Form.Item label="规则严重级别" name="severity">
                    <Radio.Group>
                        {Object.keys(SEVERITY).map((key: any) => (
                            <Radio value={toNumber(key)} key={toNumber(key)}>
                                {SEVERITY[key]}
                            </Radio>
                        ))}
                    </Radio.Group>
                </Form.Item>
                <Form.Item label="规则参数" name="rule_params" style={{ marginBottom: 0 }}>
                    <Input.TextArea placeholder="请输入规则参数" />
                </Form.Item>
            </Form>
        </Modal>
  );
};

export default EditRuleModal;
