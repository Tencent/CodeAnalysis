import React from 'react';
import { useTranslation } from 'react-i18next';
import classnames from 'classnames';
import Cookies from 'universal-cookie';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';
import { Popover, message } from 'coding-oa-uikit';

// 项目内
import s from './style.scss';

const COOKIE_NAME = 'i18next';
const DEFAULT_LANG = 'zh-CN';
const LANG = [
  { key: 'zh-CN', name: '中文（简体）' },
  { key: 'zh-TW', name: '中文（繁体）' },
  { key: 'en-US', name: 'English(US)' },
];
const cookies = new Cookies();

const LanguageUI = () => {
  const { t, i18n } = useTranslation();
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

  return (
    <Popover
      placement="left"
      content={
        <>
          <div className={s.title}>{t('切换语言')}</div>
          {LANG.map(({ key, name }) => (
            <div onClick={() => onChange(key)} className={classnames(s.item)} key={key}>
              {name}
            </div>
          ))}
        </>
      }
    >
      <div>
        {t('切换语言')}{' '}
        <span className={s.curLanguage}>
          {langText} <AngleRight />
        </span>
      </div>
    </Popover>
  );
};

export default LanguageUI;
