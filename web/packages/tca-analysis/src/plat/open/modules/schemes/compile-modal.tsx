// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案-代码检查-编译配置
 */
import React from 'react';
import { Modal, Form, Input } from 'coding-oa-uikit';

interface CompileConfigProps {
  visible: boolean;
  data: any;
  onOk: (params: any) => void;
  onClose: () => void;
}
const CompileConfig = ({ visible, data, onOk, onClose }: CompileConfigProps) => {
  const [form] = Form.useForm();

  const onFinish = (data: any) => {
    onOk(data);
  };

  return (
    <Modal
      title='编译配置'
      visible={visible}
      onCancel={onClose}
      afterClose={() => form.resetFields()}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form
        layout="vertical"
        form={form}
        initialValues={data}
        onFinish={onFinish}
      >
        <Form.Item
          name="pre_cmd"
          label="前置命令"
        >
          <Input.TextArea rows={3} placeholder="编译之前执行的命令" />
        </Form.Item>
        <Form.Item
          name="build_cmd"
          label="编译命令"
        >
          <Input.TextArea rows={3} placeholder="编译启动命令，建议不要超过5行" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CompileConfig;
