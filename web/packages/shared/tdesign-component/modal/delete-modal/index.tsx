// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 确认删除操作弹框
 */

import React, { useEffect, useState, useRef } from 'react';
import { Dialog, Form, Input, message, Button } from 'tdesign-react';
import { useTranslation } from 'react-i18next';

import s from './style.scss';

const { FormItem } = Form;

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
  const formRef = useRef<any>(null);
  const { t } = useTranslation();
  const [confirmed, setConfirmed] = useState<boolean>(false);

  useEffect(() => {
    visible && setConfirmed(false);
  }, [visible]);

  /**
  * 表单提交操作
  */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true) {
        const formData = formRef.current?.getFieldsValue(true);
        if (formData?.confirm === confirmName) {
          onOk();
        } else {
          message.error(t('验证失败，请重新输入'));
        }
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
    <Dialog
      header={`${actionType}${objectType}`}
      visible={visible}
      onConfirm={onSubmitHandle}
      onClose={onCancel}
      className={s.deleteModal}
      footer={[
        <Button
          key="back"
          variant='outline'
          onClick={onCancel}
        >
          {t('取消')}
        </Button>,
        <Button
          key="submit"
          theme="danger"
          disabled={!confirmed}
          onClick={onSubmitHandle}
        >
          {t('确认')}{actionType}
        </Button>,
      ]}
      destroyOnClose
    >
      <p className={s.warningMessage}>
            {t('您正在')}{actionType}{objectType} <span className={s.confirmText}>{confirmName}</span>{' '}<br/>
      </p>
      {addtionInfo && <p className={s.warningMessage}>{addtionInfo}</p>}
      <p className={s.confirmMessage}>{t(`为确认${actionType}操作，请输入您要${actionType}的`)}{objectType}{t('名称')}</p>
      <Form
        layout="vertical"
        ref={formRef}
        onValuesChange={checkConfirm}
      >
        <FormItem
          label=''
          name="confirm"
          rules={[{ required: true, message: t('必须输入确认信息！') }]}
          className={s.confirmInput}
        >
          <Input placeholder={confirmName} />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default DeleteModal;
