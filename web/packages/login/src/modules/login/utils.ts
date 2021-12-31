import { message } from 'coding-oa-uikit';
import { t } from '@src/i18n/i18next';

// 项目内
import { xssRedirectUri } from '@src/utils';
import { UKEY, ACCESS_TOEKN } from './constants';
/**
 * 清空登录的storage
 */
export const clearLoginLocalStorage = () => {
  localStorage.removeItem(UKEY);
  localStorage.removeItem(ACCESS_TOEKN);
};


/**
 * 登录成功操作
 * @param redirect 重定向地址
 * @param token token
 * @param msg 结果
 */
export const loginSuccessHandle = (redirect: string, token: string, msg: string = t('登录成功')) => {
  localStorage.setItem(ACCESS_TOEKN, token);
  localStorage.removeItem(UKEY);
  const timer = setTimeout(() => {
    message.success(msg);
    window.location.href = redirect ? xssRedirectUri(redirect) : '/';
    clearTimeout(timer);
  }, 1000);
};
