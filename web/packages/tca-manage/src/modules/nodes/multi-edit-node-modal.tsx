/**
 * 批量编辑节点信息弹框
 */
import React, { useRef, useState } from 'react';
import { some, get } from 'lodash';
import { Dialog, Form, Select, Loading, MessagePlugin, FormInstanceFunctions } from 'tdesign-react';
import { t } from '@src/utils/i18n';

import { putMultiNode } from '@src/services/nodes';
import { NodeMultiEditFormItem } from '@src/constant/node';
import s from './style.scss';

const { FormItem } = Form;

interface MultiEditNodeModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  selectedNodes: any;
  editItems: Array<NodeMultiEditFormItem>;
}

const MultiEditNodeModal = ({
  visible, onOk, onCancel, selectedNodes, editItems,
}: MultiEditNodeModalProps) => {
  const [loading, setLoading] = useState<boolean>(false);
  const formRef = useRef<FormInstanceFunctions>(null);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        const formData = formRef.current?.getFieldsValue(true);
        if (some(editItems, (item: NodeMultiEditFormItem) => (get(formData, item.name)))) {
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

  /** 重置表单操作 */
  const onReset = () => {
    formRef.current?.reset();
  };

  return (
    <Dialog
      header={t('批量编辑节点信息')}
      visible={visible}
      width={500}
      onConfirm={onSubmitHandle}
      onClose={onCancel}
      onOpened={onReset}
      onClosed={onReset}
    >
      <Loading loading={loading}>
        <Form
          layout='vertical'
          ref={formRef}
          labelWidth={120}
          resetType='initial'
        >
          {editItems.map((formItem: NodeMultiEditFormItem) => (
            <FormItem
              key={`multi_edit_node_${formItem.name}`}
              name={formItem.name}
              label={<>{formItem.label}<span className={s.optionalMark}>{t('（可选）')}</span></>}
            >
              <Select options={formItem.options} multiple={formItem.multiSelect}/>
            </FormItem>
          ))}
        </Form>
      </Loading>
    </Dialog>
  );
};

export default MultiEditNodeModal;
