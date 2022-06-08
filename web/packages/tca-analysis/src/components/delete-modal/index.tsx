// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 确认删除操作弹框
 */

import React, { useEffect, useState } from 'react';
import { Modal, Form, Input, message, Button } from 'coding-oa-uikit';
import { t } from '@src/i18n/i18next';

import s from './style.scss';

interface DeleteModalProps {
  deleteType: string;
  confirmName: string;
  visible: boolean;
  onCancel: () => void;
  onOk: () => void;
}

const DeleteModal = ({ deleteType, confirmName, visible, onCancel, onOk }: DeleteModalProps) => {
  const [form] = Form.useForm();
  const [confirmed, setConfirmed] = useState<boolean>(true);

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
      title={t(`删除${deleteType}`)}
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
          {t('确认删除')}
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
            {t('您正在删除')}{deleteType} <span className={s.confirmText}>{confirmName}</span>{' '}
      </p>
      <p className={s.confirmMessage}>{t('请输入您要删除的')}{deleteType}{t('的名称')}</p>
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
