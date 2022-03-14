// 请确保 i18n 初始化文件最先加载
import i18next from 'i18next';
import { initReactI18next } from 'react-i18next';
import Cookie from 'universal-cookie';

const cookie = new Cookie();
const language = cookie.get('language') || 'zh_CN';

let translation = {};

try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  translation = require(`./locales/${language}/translation.json`);
} catch (e) {
  translation = {};
}

const resources = {
  zh_CN: {
    translation,
  },
  en_US: {
    translation,
  },
};

i18next.use(initReactI18next).init({
  lng: 'zh_CN',
  keySeparator: false,
  nsSeparator: false,
  interpolation: {
    escapeValue: false,
  },
  resources,
});

export const isEnglish = () => language === 'en_US';

export default i18next;
