import React, { useEffect, useState } from 'react';
import { Modal, Form, message, Select, Spin } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { putMultiNode } from '@src/services/nodes';

// 模块内
import s from './style.scss';

const { Option } = Select;

interface MultiNodeModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  selectedNodes: any;
  tagOptions: Array<any>;
  members: Array<any>;
}

const MultiNodeModal = ({ visible, onOk, onCancel, selectedNodes, tagOptions, members }: MultiNodeModalProps) => {
  const [loading, setLoading] = useState<boolean>(false);
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
      if (formData.related_managers || formData.exec_tags) {
        setLoading(true);
        putMultiNode({node_ids: selectedNodes, ...formData}).then(() => {
          message.success(t('批量更新节点信息成功'));
          onOk();
        }).catch(() => {
          message.error(t('批量更新节点信息失败'));
        }).finally(() => {
          setLoading(false);
        });
      } else {
        message.warning(t('节点信息无更新'));
        onCancel();
      }
    });
  };

  return (
    <Modal
      forceRender
      title={t('批量编辑节点信息')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Spin spinning={loading}>
        <Form layout={'vertical'} form={form}>
          <Form.Item
            name="exec_tags"
            label={<>{t('标签')}<span className={s.optionalMark}>{t('（可选）')}</span></>}
          >
            <Select mode="multiple">
              {tagOptions.map((item: any) => (
                <Option key={item.value} value={item.value}>
                  {item.text}
                </Option>
              ))}
            </Select>
          </Form.Item>
          <Form.Item
            name="related_managers"
            label={<>{t('关注人')}<span className={s.optionalMark}>{t('（可选）')}</span></>}
          >
            <Select mode="multiple">
              {members.map((item: any) => (
                <Option key={item.username} value={item.username}>
                  {item.nickname}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Form>
      </Spin>
    </Modal>
  );
};

export default MultiNodeModal;
