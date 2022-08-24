import { throttle } from 'lodash';
import { MessagePlugin } from 'tdesign-react';

/**
 * 重新登录
 * @param content 重新登录提示信息
 * @param href 重新登录页面，默认跳转到登录页面
 */
export const reLogin = throttle((content: string, href = `/login?redirect_uri=${encodeURIComponent(window.location.href)}`) => {
  MessagePlugin.warning(content);
  const timer = setTimeout(() => {
    clearTimeout(timer);
    window.location.href = href;
  }, 300);
}, 1000);

export * from './getRoutePath';
export * from './tool';
