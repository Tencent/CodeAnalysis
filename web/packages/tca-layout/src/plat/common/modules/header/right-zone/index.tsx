import React from 'react';
import { Space, Button, Popup } from 'tdesign-react';
import { LogoGithubIcon, HelpCircleIcon } from 'tdesign-icons-react';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';

import { getDocURL } from '@plat/util';
import { User } from '@plat/modules/header/expand';

import Message from './message';
import s from '../style.scss';

// github url，用于标记是否显示开源地址
const GITHUB_URL = getMetaContent('GITHUB_URL');

const RightZone = () => <Space align='center'>
  <Message />
  {GITHUB_URL && <Popup content='开源地址' placement='bottom' showArrow destroyOnClose>
    <Button
      className={s.headerMenuItem}
      shape='square'
      size='large'
      variant='text'
      href={GITHUB_URL}
      target='_blank'
      icon={<LogoGithubIcon />}
    />
  </Popup>}
  <Popup content='帮助文档' placement='bottom' showArrow destroyOnClose>
    <Button
      className={s.headerMenuItem}
      shape='square'
      size='large'
      variant='text'
      href={getDocURL()}
      target='_blank'
      icon={<HelpCircleIcon />}
    />
  </Popup>
  <User />
</Space>;
export default RightZone;
