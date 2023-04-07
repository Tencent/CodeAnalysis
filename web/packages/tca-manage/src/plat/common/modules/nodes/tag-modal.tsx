import React, { useRef, useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { Dialog, Form, Input, MessagePlugin, Select, Tag } from 'tdesign-react';

// 项目内
import { tagAPI } from '@src/services/nodes';

// 模块内
import { TAG_TYPE_OPTIONS, TagTypeEnum } from '@src/constant/node';
import { ORG_STATUS_CHOICES, OrgStatusEnum } from '@plat/modules/orgs/constants';
import s from '@src/modules/nodes/style.scss';

const { FormItem } = Form;
const { Option } = Select;

interface TagModalProps {
  tagInfo: any;
  orgList: any;
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
}

const TagModal = ({ tagInfo, orgList, visible, onOk, onCancel }: TagModalProps) => {
  const formRef = useRef<any>(null);
  const [tagType, setTagType] = useState<number>();

  useEffect(() => {
    setTagType(tagInfo?.tag_type);
  }, [tagInfo?.tag_type]);

  const onSaveRequest = (formData: any) => {
    if (tagInfo) {
      if (formData.tag_type === TagTypeEnum.PUBLIC) {
        formData.org_sid = null;
      }
      return tagAPI.update(tagInfo.id, formData).then((response) => {
        MessagePlugin.success(t('已更新标签信息'));
        return response;
      });
    }
    return tagAPI.create(formData).then((response) => {
      MessagePlugin.success(t('已添加标签'));
      return response;
    });
  };

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        onSaveRequest(formRef.current?.getFieldsValue(true)).then(() => {
          onOk();
        });
      }
    });
  };

  const onDisplayNameFocus = () => {
    const tagName = formRef.current?.getFieldValue('name');
    const tagDisplayName = formRef.current?.getFieldValue('display_name');
    if (!tagInfo && !tagDisplayName) {
      formRef.current?.setFieldsValue({ display_name: tagName });
    }
  };

  const onChangeTagType = (value: number) => {
    setTagType(value);
  };

  return (
    <Dialog
      header={tagInfo ? t('更新标签') : t('添加标签')}
      visible={visible}
      onConfirm={onSubmitHandle}
      onClose={onCancel}
      destroyOnClose
    >
      <Form
        layout='vertical'
        ref={formRef}
        resetType='initial'
      >
        <FormItem
          name="name"
          label={t('标签名称')}
          initialData={get(tagInfo, 'name')}
          rules={[{ required: true, message: t('标签名称为必填项') }]}
        >
          <Input />
        </FormItem>
        <FormItem
          name="display_name"
          label={t('展示名称')}
          initialData={get(tagInfo, 'display_name')}
          rules={[{ required: true, message: t('展示名称为必填项') }]}
        >
          <Input onFocus={onDisplayNameFocus} />
        </FormItem>
        <FormItem
          name="tag_type"
          label={t('标签类型')}
          initialData={get(tagInfo, 'tag_type')}
          rules={[{ required: true, message: t('标签类型为必选项') }]}
        >
          <Select onChange={onChangeTagType}>
            {TAG_TYPE_OPTIONS.map((item: any) => (
              // 不允许创建停用标签
              (tagInfo || item.value !== TagTypeEnum.DISABLED)
              && <Option key={item.value} value={item.value} label={item.label} />
            ))}
          </Select>
        </FormItem>
        {tagType === TagTypeEnum.PRIVATE && <FormItem
          name="org_sid"
          label={t('所属团队')}
          rules={[{ required: true, message: t('所属团队为必选项') }]}
          initialData={get(tagInfo, 'org_sid')}
        >
          <Select>
            {orgList.map((item: any) => (
              <Option key={item.org_sid} value={item.org_sid} label={item.name}>
                <div className={s.orgOption}>
                  <span>{item.name}</span>
                  {item.status === OrgStatusEnum.ACTIVE
                    ? <Tag size='small' className={s.activeOrg}>{ORG_STATUS_CHOICES[OrgStatusEnum.ACTIVE]}</Tag>
                    : <Tag size='small' className={s.inactiveOrg}>{ORG_STATUS_CHOICES[OrgStatusEnum.FORBIDEN]}</Tag>
                  }
                </div>
              </Option>
            ))}
          </Select>
        </FormItem>}
        <FormItem
          name="desc"
          label={t('标签描述')}
          initialData={get(tagInfo, 'desc')}
        >
          <Input />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default TagModal;
