import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Modal, Form, Input, message, Select } from 'coding-oa-uikit';

// 项目内
import { postTags, putTag } from '@src/services/nodes';

// 模块内
import { TAG_TYPE_OPTIONS } from '@src/constant';

const { Option } = Select;

interface IProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  taginfo: any;
}

const TagModal = ({ taginfo, visible, onOk, onCancel }: IProps) => {
  const [form] = Form.useForm();
  const { orgSid }: any = useParams();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onSaveRequest = (formData: any) => {
    if (taginfo) {
      return putTag(orgSid, taginfo.id, formData).then((response) => {
        message.success(t('已更新标签信息'));
        return response;
      });
    }
    return postTags(orgSid, formData).then((response) => {
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
        {taginfo && <Form.Item
          name="name"
          label={t('标签名称')}
        >
          <Input disabled/>
        </Form.Item>}
        <Form.Item
          name="display_name"
          label={t('展示名称')}
          rules={[{ required: true, message: t('展示名称为必填项') }]}
        >
          <Input />
        </Form.Item>
        {taginfo && <Form.Item
          name="tag_type"
          label={t('类型')}
          rules={[{ required: true, message: t('标签类型为必选项') }]}
        >
          <Select>
            {TAG_TYPE_OPTIONS.slice(1, 3).map((item: any) => (
              <Option key={item.value} value={item.value}>
                {item.label}
              </Option>
            ))}
          </Select>
        </Form.Item>}
        <Form.Item name="desc" label={t('标签描述')}>
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TagModal;
