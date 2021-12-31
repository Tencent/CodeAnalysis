import React, { useState } from 'react';
import Cookies from 'universal-cookie';
import { message, Menu, Dropdown, Button } from 'coding-oa-uikit';

import Globe from 'coding-oa-uikit/lib/icon/Globe';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';
import { t } from '@src/i18n/i18next';
import s from './style.scss';

const COOKIE_NAME = 'language';
const DEFAULT_LANG = 'zh_CN';
const LANG = [
  { key: 'zh_CN', name: '中文（简体）' },
  { key: 'zh_TW', name: '中文（繁体）' },
  { key: 'en_US', name: 'English(US)' },
];
const cookies = new Cookies();

const LanguageUI = () => {
  const [lang, setLang] = useState(cookies.get(COOKIE_NAME) || DEFAULT_LANG);

  const onChange = (key: string) => {
    cookies.set(COOKIE_NAME, key);
    setLang(key);
    message.loading(t('语言切换中...'));
    const timer = setTimeout(() => {
      window.location.reload();
      clearTimeout(timer);
    }, 300);
  };

  const { name: langText = '' } = LANG.find(({ key }) => lang === key) || {};

  return (
    <Dropdown
      className={s.languageDropdown}
      overlay={
        <Menu>
          {LANG.map(item => (
            <Menu.Item key={item.key} onClick={() => onChange(item.key)}>
              {item.name}
            </Menu.Item>
          ))}
        </Menu>
      }
      placement="topCenter"
    >
      <Button type="text">
        <Globe /> {langText} <AngleUp />
      </Button>
    </Dropdown>
  );
};

export default LanguageUI;
