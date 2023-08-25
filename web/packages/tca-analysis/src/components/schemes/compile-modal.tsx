// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 编译配置
 */
import React from 'react';
import { Dialog, Form, Textarea } from 'tdesign-react';
import CompileTip from '@plat/modules/schemes/compile-tip';

const { FormItem } = Form;

interface CompileConfigProps {
  visible: boolean;
  data: any;
  onOk: (params: any) => void;
  onClose: () => void;
}
const CompileConfig = ({ visible, data, onOk, onClose }: CompileConfigProps) => {
  const [form] = Form.useForm();

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validate().then((result: any) => {
      if (result === true) {
        onOk(form?.getFieldsValue(true));
      }
    });
  };

  return (
    <Dialog
      header='编译配置'
      visible={visible}
      onClose={onClose}
      onConfirm={onSubmitHandle}
      width={420}
    >
      <CompileTip />
      <Form
        layout="vertical"
        labelAlign='top'
        form={form}
        initialData={data}
      >
        <FormItem
          name="pre_cmd"
          label="前置命令"
        >
          <Textarea rows={3} placeholder="编译之前执行的命令" />
        </FormItem>
        <FormItem
          name="build_cmd"
          label="编译命令"
        >
          <Textarea rows={3} placeholder="编译启动命令，建议不要超过5行" />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default CompileConfig;
