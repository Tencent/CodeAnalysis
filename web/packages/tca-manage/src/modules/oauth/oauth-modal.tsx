import React, { useEffect } from 'react';
import { Modal, Form, Input, Select } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import { SCM_PLATFORM_OPTIONS } from './constants';

interface IProps {
  visible: boolean;
  scminfo: any;
  onCancel: () => void;
  onOk: ( formData:any ) => void;
}


const OAuthModal = ({ scminfo, visible, onCancel, onOk }: IProps) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);


  /**
     * 表单保存操作
     * @param formData 参数
     */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      onOk(formData);
      console.log(formData);
    });
  };

  return (
    <Modal
      forceRender
      title={scminfo ? t('更新配置') : t('创建配置')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Form layout={'vertical'} form={form} initialValues={scminfo || {}}>
        <Form.Item name="scm_platform" label="平台类型">
          <Select options={SCM_PLATFORM_OPTIONS} defaultValue={2}/>
        </Form.Item>
        <Form.Item
          name="client_id"
          label={t('Client ID')}
          rules={[{ required: true, message: t('Client ID为必填项') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="client_secret"
          label={t('Client Secret')}
          rules={[{ required: true, message: t('Client Secret为必填项') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="redirect_uri"
          label={t('回调地址')}
          rules={[{ required: true, message: t('回调地址为必填项') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="scm_platform_des"
          label={t('平台描述')}
        >
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default OAuthModal;
