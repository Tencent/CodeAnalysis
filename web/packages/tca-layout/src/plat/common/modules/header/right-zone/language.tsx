import React from 'react';
import i18n from 'i18next';
import Cookies from 'universal-cookie';
import { t } from '@src/utils/i18n';
import { message, Popup } from 'tdesign-react';
import { ChevronLeftIcon } from 'tdesign-icons-react';

// 项目内
import s from '../style.scss';

const COOKIE_NAME = 'i18next';
const DEFAULT_LANG = 'zh-CN';
const LANG = [
  { key: 'zh-CN', name: '中文（简体）' },
  { key: 'zh-TW', name: '中文（繁体）' },
  { key: 'en-US', name: 'English(US)' },
];
const cookies = new Cookies();

const Language = () => {
  const lang = cookies.get(COOKIE_NAME) ?? DEFAULT_LANG;
  const { name: langText = '' } = LANG.find(({ key }) => lang === key) || {};

  const onChange = (key: string) => {
    i18n.changeLanguage(key);
    message.loading(t('语言切换中...'));
    const timer = setTimeout(() => {
      clearTimeout(timer);
      window.location.reload();
    }, 300);
  };

  return <Popup trigger="hover" showArrow placement='left' content={<div className={s.headerDropdownPopover}>
    <div className={s.title}>{t('切换语言')}</div>
    {LANG.map(({ key, name }) => (
      <div onClick={() => onChange(key)} className={s.item} key={key}>
        {name}
      </div>
    ))}
  </div>}>
    <div className={s.headerDropItem}>
      <ChevronLeftIcon className={s.icon} />
      <span>切换语言</span>
      <span className={s.rightValue}>{langText}</span>
    </div>
  </Popup>;
};

export default Language;
