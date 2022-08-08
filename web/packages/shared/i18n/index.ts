import i18n, { InitOptions } from 'i18next';
import Backend from 'i18next-http-backend';
import LanguageDetector from 'i18next-browser-languagedetector';
import Log from '../util/log';

export interface InitI18next {
  /** init i18n参数 */
  options?: InitOptions
  /** use i18n模块 */
  modules?: any[]
}

/**
 * 初始化i18n
 * @param param0 {options, modules} 参数配置
 * @returns 初始化i18n
 *
 * 注：默认modules已使用i18next-http-backend, i18next-browser-languagedetector
 * react使用i18n时，需要将react-i18next的initReactI18next传递至modules中，
 */
const initI18next = ({ options, modules = [] }: InitI18next) => {
  const i18nModules = [Backend, LanguageDetector, ...modules];
  i18nModules.forEach((module) => {
    i18n.use(module);
  });
  const i18nOptions: InitOptions = {
    react: {
      useSuspense: false,
    },
    fallbackLng: 'zh-CN', // 未找到最终匹配zh_CN
    interpolation: {
      escapeValue: false,
    },
    detection: {
      // caches: ['localStorage', 'cookie'],
      caches: ['cookie'],
    },
    ...options,
  };

  return i18n.init(i18nOptions, (err) => {
    Log.info('i18n插件初始化完毕', err);
  });
};

export default initI18next;
export const t = i18n.t.bind(i18n);
