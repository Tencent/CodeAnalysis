import React from 'react';
import { Button, Badge, Popup } from 'tdesign-react';
import { MailIcon } from 'tdesign-icons-react';

import { MessageInterceptor } from '@plat/modules/header/expand';
import s from '../style.scss';

interface MessageProps {
  enable?: boolean;
  count: number;
  onClick: () => void;
}

const Message = ({ count, onClick, enable = false }: MessageProps) => {
  if (enable) {
    return <Popup content='通知消息' placement='bottom' showArrow destroyOnClose><Badge count={count} dot={false} shape='circle' showZero={false} size='small'>
      <Button className={s.headerMenuItem} shape='square' size='large' variant='text' icon={<MailIcon />}
        onClick={onClick}
      />
    </Badge></Popup>;
  }
  return <></>;
};

export default MessageInterceptor(Message);
