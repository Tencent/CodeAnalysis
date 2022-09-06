import React from 'react';
import { useTranslation } from 'react-i18next';

import { Modal, Form, Input, message } from 'coding-oa-uikit';
import { createProject } from '@src/services/team';

interface CreateProjectProps {
  orgSid: string;
  visible: boolean;
  onClose: () => void;
  callback: () => void;
}

const CreateProject = (props: CreateProjectProps) => {
  const { orgSid, visible, onClose, callback } = props;
  const { t } = useTranslation();
  const [form] = Form.useForm();

  const onFinish = (formData: any) => {
    createProject(orgSid, formData).then(() => {
      message.success(t('创建成功'));
      onClose();
      callback();
    });
  };

  return (
    <Modal
      title={t('创建项目')}
      width={520}
      visible={visible}
      // okButtonProps={{ loading }}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form layout={'vertical'} form={form}>
        <Form.Item
          name="name"
          label={t('项目唯一标识')}
          rules={[{
            required: true,
            message: t('项目唯一标识为必填项'),
          }, {
            pattern: /^[A-Za-z0-9_-]+$/,
            message: t('仅支持英文、数字、中划线或下划线'),
          }]}
        >
          <Input placeholder={t('仅支持英文、数字、中划线或下划线')} />
        </Form.Item>
        <Form.Item
          name="display_name"
          label={t('项目名称')}
          rules={[{ required: true, message: t('项目名称为必填项') }]}
        >
          <Input onFocus={() => {
            form.setFieldsValue({
              display_name: form.getFieldValue('name'),
            });
          }} />
        </Form.Item>
        <Form.Item name="description" label={t('项目描述')}>
          <Input.TextArea />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateProject;
