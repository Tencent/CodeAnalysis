import { throttle } from 'lodash';
import { message } from 'coding-oa-uikit';
import { getMetaContent, isTrue } from '@tencent/micro-frontend-shared/util';

export * from './init-request';
export * from './user';
export * from './matomo';

/**
 * 重新登录
 * @param content 重新登录提示信息
 * @param href 重新登录页面，默认跳转到登录页面
 */
export const reLogin = throttle((content: string, href = `/login?redirect_uri=${encodeURIComponent(window.location.href)}`) => {
  message.warning(content);
  const timer = setTimeout(() => {
    clearTimeout(timer);
    window.location.href = href;
  }, 300);
}, 1000);

/** 判断是否是管理后台 */
export const isEnableManage = () => isTrue(getMetaContent('ENABLE_MANAGE', process.env.ENABLE_MANAGE));

/** 获取帮助文档首页链接 */
export const getDocURL = () => '/document/';

/** 获取帮助文档开放API页链接 */
export const getApiDocURL = () => '/document/zh/api/';
