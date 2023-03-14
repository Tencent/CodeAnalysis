import initI18next from '@tencent/micro-frontend-shared/i18n';
import en from '@src/locales/en-US/translation.json';
import zh from '@src/locales/zh-CN/translation.json';

// 初始化i18n
const i18n = initI18next({ modules: [], options: {
  resources: {
    'en-US': { translation: en },
    'zh-CN': { translation: zh },
  },
} });

export const t = i18n.t.bind(i18n);
