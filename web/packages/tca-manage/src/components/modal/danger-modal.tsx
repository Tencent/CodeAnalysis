// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { ReactNode } from 'react';
import { Modal, Button } from 'coding-oa-uikit';
// 项目内
import { t } from '@src/i18n/i18next';

interface IProps {
  title: string;
  visible: boolean;
  onCancel: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
  onOk: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
  content?: ReactNode;
}

const DangerModal = (props: IProps) => {
  const { visible, title, onCancel, onOk, content } = props;

  return (
    <Modal
      visible={visible}
      title={title}
      onCancel={onCancel}
      footer={[
        <Button key="submit" type="primary" danger onClick={onOk}>
          {t('确认删除')}
        </Button>,
        <Button key="back" onClick={onCancel}>
          {t('取消')}
        </Button>,
      ]}
    >
      {content}
    </Modal>
  );
};

export default DangerModal;
