import React from 'react';
import { t } from '@src/utils/i18n';
import i18n from 'i18next';
import Cookies from 'universal-cookie';
import { MessagePlugin, Dropdown, Button } from 'tdesign-react';
import { InternetIcon, ChevronUpIcon } from 'tdesign-icons-react';
// 项目内
import s from '@src/style.scss';

const { DropdownMenu, DropdownItem } = Dropdown;

const COOKIE_NAME = 'i18next';
const DEFAULT_LANG = 'zh-CN';
const LANG = [
  { key: 'zh-CN', name: '中文（简体）' },
  { key: 'zh-TW', name: '中文（繁体）' },
  { key: 'en-US', name: 'English(US)' },
];
const cookies = new Cookies();

const LanguageUI = () => {
  const lang = cookies.get(COOKIE_NAME) ?? DEFAULT_LANG;

  const onChange = (key: string) => {
    i18n.changeLanguage(key);
    MessagePlugin.loading(t('语言切换中...'));
    const timer = setTimeout(() => {
      clearTimeout(timer);
      window.location.reload();
    }, 300);
  };

  const { name: langText = '' } = LANG.find(({ key }) => lang === key) || {};

  return (
    <Dropdown
      placement="top"
    >
      <Button variant='text' className={s.languageDropdown}>
        <span style={{ display: 'flex', alignItems: 'center' }}>
          <InternetIcon/> {langText} <ChevronUpIcon />
        </span>
      </Button>
      <DropdownMenu>
        {LANG.map(item => (
          <DropdownItem key={item.key} value={item.key} onClick={() => onChange(item.key)}>
            {item.name}
          </DropdownItem>
        ))}
      </DropdownMenu>
    </Dropdown>
  );
};

export default LanguageUI;
