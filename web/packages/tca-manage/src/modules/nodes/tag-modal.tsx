import React, { useEffect } from 'react';
import { Modal, Form, Input, message } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { postTags, putTag } from '@src/services/nodes';

// 模块内

interface IProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  taginfo: any;
}

const TagModal = ({ taginfo, visible, onOk, onCancel }: IProps) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onSaveRequest = (formData: any) => {
    if (taginfo) {
      return putTag(taginfo.id, formData).then((response) => {
        message.success(t('已更新标签信息'));
        return response;
      });
    }
    return postTags(formData).then((response) => {
      message.success(t('已创建标签'));
      return response;
    });
  };

  /**
     * 表单保存操作
     * @param formData 参数
     */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      // 暂时标签仅能设置为公有
      formData.public = true
      onSaveRequest(formData).then(() => {
        onOk();
      });
    });
  };

  return (
    <Modal
      forceRender
      title={taginfo ? t('更新标签') : t('添加标签')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Form layout={'vertical'} form={form} initialValues={taginfo || { public: true }}>
        <Form.Item
          name="name"
          label={t('标签名称')}
          rules={[{ required: true, message: t('标签名称为必填项') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item name="desc" label="标签描述">
          <Input />
        </Form.Item>
        {/* <Form.Item name="public" label="是否公用" valuePropName="checked">
          <Switch disabled />
        </Form.Item> */}
      </Form>
    </Modal>
  );
};

export default TagModal;
