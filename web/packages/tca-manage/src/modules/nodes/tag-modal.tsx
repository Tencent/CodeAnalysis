import React, { useEffect } from 'react';
import { Modal, Form, Input, message, Select, Tag } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { postTags, putTag } from '@src/services/nodes';
import { ORG_STATE_CHOICES, ORG_STATE_ENUM } from '../orgs/constants';

// 模块内
import { TAG_TYPE_OPTIONS, TAG_TYPE_ENUM } from './constants';
import s from './style.scss';

const { Option } = Select;

interface TagModalProps {
  tagInfo: any;
  orgList: any;
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
}

const TagModal = ({ tagInfo, orgList, visible, onOk, onCancel }: TagModalProps) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onSaveRequest = (formData: any) => {
    if (tagInfo) {
      if (formData.tag_type === TAG_TYPE_ENUM.PUBLIC) {
        formData.org_sid = null;
      }
      return putTag(tagInfo.id, formData).then((response) => {
        message.success(t('已更新标签信息'));
        return response;
      });
    }
    return postTags(formData).then((response) => {
      message.success(t('已添加标签'));
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

  const onDisplayNameFocus = () => {
    const tagName = form.getFieldValue('name');
    const tagDisplayName = form.getFieldValue('display_name');
    if (!tagInfo && !tagDisplayName) {
      form.setFieldsValue({ display_name: tagName });
    }
  };

  return (
    <Modal
      forceRender
      title={tagInfo ? t('更新标签') : t('添加标签')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Form layout={'vertical'} form={form} initialValues={tagInfo || { public: true }}>
        <Form.Item
          name="name"
          label={t('标签名称')}
          rules={[{ required: true, message: t('标签名称为必填项') }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          name="display_name"
          label={t('展示名称')}
          rules={[{ required: true, message: t('展示名称为必填项') }]}
        >
          <Input onFocus={onDisplayNameFocus}/>
        </Form.Item>
        <Form.Item
          name="tag_type"
          label="类型"
          rules={[{ required: true, message: t('标签类型为必选项') }]}
        >
          <Select>
            {TAG_TYPE_OPTIONS.map((item: any) => (
              // 不允许创建停用标签
              (tagInfo || item.value !== TAG_TYPE_ENUM.DISABLED)
              && <Option key={item.value} value={item.value}>
                {item.text}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, curValues) => prevValues.tag_type !== curValues.tag_type}
        >
          {({ getFieldValue }) => {
              const tagType = getFieldValue('tag_type');
              return tagType === TAG_TYPE_ENUM.PRIVATE && (
                <Form.Item
                  name="org_sid"
                  label="所属团队"
                  rules={[{ required: true, message: t('所属团队为必选项') }]}
                >
                  <Select showSearch optionFilterProp='label'>
                    {orgList.map((item: any) => (
                      <Option key={item.org_sid} value={item.org_sid} label={item.name}>
                        <div className={s.orgOption}>
                          <span>{item.name}</span>
                          {item.status === ORG_STATE_ENUM.ACTIVE
                            ? <Tag className={s.activeOrg}>{ORG_STATE_CHOICES[ORG_STATE_ENUM.ACTIVE]}</Tag>
                            : <Tag className={s.inactiveOrg}>{ORG_STATE_CHOICES[ORG_STATE_ENUM.INACTIVE]}</Tag>
                          }
                        </div>
                      </Option>
                    ))}
                  </Select>
                </Form.Item>
              );
          }}
        </Form.Item>
        <Form.Item name="desc" label="标签描述">
          <Input />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default TagModal;
