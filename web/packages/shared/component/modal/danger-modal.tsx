import React, { ReactNode } from 'react';
import { Modal, Button } from 'coding-oa-uikit';

interface IProps {
  title: string;
  visible: boolean;
  onCancelText?: string;
  onCancel: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
  onOkText?: string;
  onOk: (e: React.MouseEvent<HTMLElement, MouseEvent>) => void;
  content?: ReactNode;
}

const DangerModal = (props: IProps) => {
  const { visible, title, onCancel, onCancelText = '取消', onOk, onOkText = '确认', content } = props;

  return (
    <Modal
      visible={visible}
      title={title}
      onCancel={onCancel}
      footer={[
        <Button key="submit" type="primary" danger onClick={onOk}>
          {onOkText}
        </Button>,
        <Button key="back" onClick={onCancel}>
          {onCancelText}
        </Button>,
      ]}
    >
      {content}
    </Modal>
  );
};

export default DangerModal;
