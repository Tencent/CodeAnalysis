// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * utils 工具类
 */
import Moment from 'moment';
import { forEach, pick, get, throttle } from 'lodash';

import qs from 'qs';
import { message } from 'coding-oa-uikit';
import { LOGIN_SERVER_API } from '@src/services/common';

/**
 * 格式化时间，默认返回时间的年月日
 * @param time 时间
 * @param format 格式化参数
 */
export const formatDate = (time: any, format = 'YYYY-MM-DD') => Moment(time, format).format(format);

/**
 * 格式化时间，返回时间的年月日，时分秒
 * @param time 时间
 */
export const formatDateTime = (time: any) => (time ? formatDate(time, 'YYYY-MM-DD HH:mm:ss') : null);

/**
 * 根据loading状态设置layout加载class，用于控制container显示/隐藏
 * @param loading 加载状态
 */
export function setLayoutCompletedClass(loading: boolean) {
  const node = document.getElementById('main-container');
  const layoutUnCompletedClass = 'layout-uncompleted';
  if (node) {
    if (loading && !node.classList.contains(layoutUnCompletedClass)) {
      node.classList.add(layoutUnCompletedClass);
    } else if (!loading && node.classList.contains(layoutUnCompletedClass)) {
      node.classList.remove(layoutUnCompletedClass);
    }
  }
}

/**
 * 根据uid获取用户头像url
 * @param uid
 */
export function gUserImgUrl(uid: string) {
  return `${LOGIN_SERVER_API}/login/users/${uid}/`;
}

/**
 * 重新登录，节流
 */
export const reLogin = throttle((content: string) => {
  message.warning(content);
  const timer = setTimeout(() => {
    window.location.href = `/login?redirect_uri=${encodeURIComponent(window.location.href)}`;
    clearTimeout(timer);
  }, 300);
}, 1000);

export function logout(content: string) {
  message.info(content);
  localStorage.removeItem('userInfo');
  localStorage.removeItem('associate_userinfo');
  localStorage.removeItem('accessToken');
  const timer = setTimeout(() => {
    window.location.href = '/';
    clearTimeout(timer);
  }, 300);
}

/**
 * 日志前缀
 */
export const LOG_PREFIX = '[Micro Frontend Layout] ';

/**
 * 提示
 * @param message 信息
 * @param optionalParams 其他参数
 */
export const info = (message?: any, ...optionalParams: any[]) => {
  console.info(LOG_PREFIX + message, ...optionalParams);
};

/**
 * 错误
 * @param message 信息
 * @param optionalParams 其他参数
 */
export const error = (message?: any, ...optionalParams: any[]) => {
  console.info(LOG_PREFIX + message, ...optionalParams);
};

/**
 * 警告
 * @param message 信息
 * @param optionalParams 其他参数
 */
export const warn = (message?: any, ...optionalParams: any[]) => {
  console.warn(LOG_PREFIX + message, ...optionalParams);
};

/**
 * 获取meta标签content
 * @param key
 * @param defaultValue
 */
export const getRuntimeEnv = (key: string, defaultValue = '') => {
  const meta = document.querySelector(`meta[name=${key}]`) as HTMLMetaElement;
  return meta ? meta.content : defaultValue;
};

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

/**
 * 获取当前查询参数
 */
export const getQuery = () => qs.parse(window.location.search.replace('?', ''));

/**
 * 获取翻页后的offset和limit，用于解析Pagination
 * @param page 页码
 * @param pageSize 每页数量
 */
export const getPaginationParams = (page: number, pageSize: number) => ({
  offset: (page - 1) * pageSize,
  limit: pageSize,
});

/**
 * 获取URL参数+params参数组合成的URLSearchParams
 * @param filterFields 剔除项
 * @param params 补充参数
 */
export const getFilterURLSearchParams = (filterFields: Array<string> = [], params: any = {}) => {
  const query = new URLSearchParams(window.location.search);
  forEach(pick(params, ['limit', 'offset', 'ordering', ...filterFields]), (value, key) => {
    query.set(key, value);
  });
  return query;
};

/**
 * 获取filter后的路由
 * @param params json对象
 */
export const getFilterURLPath = (filterFields: Array<string> = [], params: any = {}) => {
  const query = getFilterURLSearchParams(filterFields, params);
  return `${window.location.pathname}?${decodeURIComponent(query.toString())}`;
};
