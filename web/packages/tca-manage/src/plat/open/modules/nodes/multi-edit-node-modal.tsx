/**
 * 批量编辑节点信息弹框
 */
import React, { useRef, useState } from 'react';
import { Dialog, Form, Select, Loading, MessagePlugin } from 'tdesign-react';
import { useTranslation } from 'react-i18next';

import { putMultiNode } from '@src/services/nodes';
import s from './style.scss';

const { FormItem } = Form;
const { Option } = Select;

interface MultiEditNodeModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  selectedNodes: any;
  tagOptions: Array<any>;
  members: Array<any>;
}

const MultiEditNodeModal = ({
  visible, onOk, onCancel, selectedNodes, tagOptions, members,
}: MultiEditNodeModalProps) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState<boolean>(false);
  const formRef = useRef<any>(null);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        const formData = formRef.current?.getFieldsValue(true);
        if (formData.related_managers || formData.exec_tags) {
          setLoading(true);
          putMultiNode({ node_ids: selectedNodes, ...formData })
            .then(() => {
              MessagePlugin.success(t('批量更新节点信息成功'));
              onOk();
            })
            .catch(() => {
              MessagePlugin.error(t('批量更新节点信息失败'));
            })
            .finally(() => {
              setLoading(false);
            });
        } else {
          MessagePlugin.warning(t('节点信息无更新'));
          onCancel();
        }
      }
    });
  };

  return (
    <Dialog
      header={t('批量编辑节点信息')}
      visible={visible}
      onClose={onCancel}
      width={500}
      onConfirm={onSubmitHandle}
      onClosed={formRef.current?.reset()}
    >
      <Loading loading={loading}>
        <Form
          layout='vertical'
          ref={formRef}
          labelWidth={120}
        >
          <FormItem
            label={<>{t('标签')}<span className={s.optionalMark}>{t('（可选）')}</span></>}
            name="exec_tags"
          >
            <Select multiple>
              {tagOptions.map((item: any) => (
                <Option key={item.value} value={item.value}>
                  {item.text}
                </Option>
              ))}
            </Select>
          </FormItem>
          <FormItem
            label={<>{t('关注人')}<span className={s.optionalMark}>{t('（可选）')}</span></>}
            name="related_managers"
          >
            <Select multiple>
              {members.map((item: any) => (
                <Option key={item.username} value={item.username}>
                  {item.nickname}
                </Option>
              ))}
            </Select>
          </FormItem>
        </Form>
      </Loading>
    </Dialog>
  );
};

export default MultiEditNodeModal;
