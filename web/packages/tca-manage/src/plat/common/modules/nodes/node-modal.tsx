import React, { useRef } from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { Dialog, Form, MessagePlugin, Input, Select } from 'tdesign-react';

// 项目内
import { nodeAPI } from '@src/services/nodes';
import { NODE_ENABLED_OPTIONS } from '@src/constant/node';

const { FormItem } = Form;

interface NodeModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  nodeinfo: any;
  tagOptions: Array<any>;
  memberOptions: Array<any>;
}

const NodeModal = ({ nodeinfo, visible, onOk, onCancel, tagOptions, memberOptions }: NodeModalProps) => {
  const formRef = useRef<any>(null);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        nodeAPI.update(nodeinfo.id, formRef.current?.getFieldsValue(true))
          .then(() => {
            MessagePlugin.success(t('已更新节点'));
            onOk();
          })
          .catch(() => {
            MessagePlugin.error(t('更新节点失败'));
          });
      }
    });
  };

  return (
    <Dialog
      header={t('更新节点')}
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
          label={t('节点名称')}
          initialData={get(nodeinfo, 'name')}
          rules={[{ required: true, message: t('节点名称为必填项') }]}
        >
          <Input />
        </FormItem>
        <FormItem
          name="addr"
          label="IP 地址"
          initialData={get(nodeinfo, 'addr')}
        >
          <Input disabled />
        </FormItem>
        <FormItem
          name="exec_tags"
          label="标签"
          initialData={get(nodeinfo, 'exec_tags')}
          rules={[{ required: true, message: t('节点标签为必选项') }]}
        >
          <Select multiple options={tagOptions} />
        </FormItem>
        <FormItem
          name="enabled"
          label="节点可用性"
          initialData={get(nodeinfo, 'enabled')}
          rules={[{ required: true, message: t('节点可用性为必选项') }]}
        >
          <Select options={NODE_ENABLED_OPTIONS} />
        </FormItem>
        <FormItem
          name="related_managers"
          label="关注人"
          initialData={get(nodeinfo, 'related_managers')}
        >
          <Select multiple options={memberOptions} />
        </FormItem>
        <FormItem
          name="manager"
          label="管理员"
          initialData={get(nodeinfo, 'manager')}
          rules={[{ required: true, message: t('管理员为必填项') }]}
        >
          <Input />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default NodeModal;
