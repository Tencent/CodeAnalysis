/**
 * utils 工具类
 */
import { MessagePlugin } from 'tdesign-react';
import { get, throttle } from 'lodash';

/**
 * 重新登录，节流
 */
export const reLogin = throttle((content: string) => {
  MessagePlugin.warning(content);
  const timer = setTimeout(() => {
    window.location.href = `/login?redirect_uri=${encodeURIComponent(window.location.href)}`;
    clearTimeout(timer);
  }, 300);
}, 1000);

export function logout(content: string) {
  MessagePlugin.info(content);
  localStorage.removeItem('userInfo');
  localStorage.removeItem('associate_userinfo');
  localStorage.removeItem('accessToken');
  const timer = setTimeout(() => {
    window.location.href = '/';
    clearTimeout(timer);
  }, 300);
}

/**
 * 获取用户名
 * @param user 用户，可能是字符串，可能是一个 user对象
 */
export const getUserName = (user: any) => {
  if (typeof user === 'string') {
    return user;
  }
  return get(user, 'nickname') || get(user, 'username') || '';
};
