import { MessagePlugin } from 'tdesign-react';
import { xssRedirectUri } from '@tencent/micro-frontend-shared/util';
import { UKEY, ACCESS_TOEKN } from '@src/constant';

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
export const loginSuccessHandler = (redirect: string, token: string, msg = '登录成功') => {
  localStorage.setItem(ACCESS_TOEKN, token);
  localStorage.removeItem(UKEY);
  const timer = setTimeout(() => {
    MessagePlugin.success(msg);
    window.location.href = redirect ? xssRedirectUri(redirect) : '/';
    clearTimeout(timer);
  }, 1000);
};
