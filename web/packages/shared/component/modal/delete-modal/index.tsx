/**
 * 确认删除操作弹框
 */

import React, { useEffect, useState } from 'react';
import { Modal, Form, Input, message, Button } from 'coding-oa-uikit';
import { useTranslation } from 'react-i18next';

import s from './style.scss';

interface DeleteModalProps {
  actionType: string;
  objectType: string;
  confirmName: string;
  visible: boolean;
  addtionInfo?: string;
  onCancel: () => void;
  onOk: () => void;
}

const DeleteModal = ({ actionType, objectType, confirmName, addtionInfo = '', visible, onCancel, onOk }: DeleteModalProps) => {
  const [form] = Form.useForm();
  const [confirmed, setConfirmed] = useState<boolean>(true);
  const { t } = useTranslation();

  useEffect(() => {
    visible && form.resetFields();
    visible && setConfirmed(false);
  }, [visible]);

  /**
   * 表单提交操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      if (formData?.confirm === confirmName) {
        onOk();
      } else {
        message.error(t('验证失败，请重新输入'));
      }
    });
  };

  const checkConfirm = (changedValues: any) => {
    if (changedValues?.confirm === confirmName) {
      setConfirmed(true);
    } else {
      setConfirmed(false);
    }
  };

  return (
    <Modal
      title={`${actionType}${objectType}`}
      visible={visible}
      onCancel={onCancel}
      className={s.deleteModal}
      footer={[
        <Button
          key="submit"
          type="primary"
          disabled={!confirmed}
          danger
          onClick={onSubmitHandle}
        >
          {t('确认')}{actionType}
        </Button>,
        <Button
          key="back"
          className="cancle-btn"
          onClick={onCancel}
        >
          {t('取消')}
        </Button>,
      ]}
    >
      <p className={s.warningMessage}>
        {t('您正在')}{actionType}{objectType} <span className={s.confirmText}>{confirmName}</span>{' '}<br/>
      </p>
      {addtionInfo && <p className={s.warningMessage}>{addtionInfo}</p>}
      <p className={s.confirmMessage}>{t(`为确认${actionType}操作，请输入您要${actionType}的`)}{objectType}</p>
      <Form
        layout="vertical"
        form={form}
        onValuesChange={checkConfirm}
      >
        <Form.Item
          label=''
          name="confirm"
          rules={[{ required: true, message: t('必须输入确认信息！') }]}
          className={s.confirmInput}
        >
          <Input placeholder={confirmName} />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default DeleteModal;
