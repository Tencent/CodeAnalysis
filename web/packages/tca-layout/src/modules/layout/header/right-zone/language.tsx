import React, { useState } from 'react';
import classnames from 'classnames';
import Cookies from 'universal-cookie';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';
// import Dropdown from '@coding/coding-ui-kit/dropdown';
// import Menu from '@coding/coding-ui-kit/menu';
import { Popover, message } from 'coding-oa-uikit';
import { t } from '@src/i18n/i18next';
// import { getMainDomain } from '@framework/utils/domain';
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
    // cookies.set(COOKIE_NAME, key, { path: '/', domain: getMainDomain() });
    cookies.set(COOKIE_NAME, key, { path: '/' });
    setLang(key);
    message.loading(t('语言切换中...'));
    const timer = setTimeout(() => {
      window.location.reload();
      clearTimeout(timer);
    }, 300);
  };

  const { name: langText = '' } = LANG.find(({ key }) => lang === key) || {};
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
