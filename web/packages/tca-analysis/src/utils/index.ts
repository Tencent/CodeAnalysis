// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import Moment from 'moment';
import qs from 'qs';
import { message } from 'coding-oa-uikit';
import { get, uniqBy, throttle, isEmpty } from 'lodash';
import { LOGIN_SERVER_API } from '@plat/api';
import { useStateStore } from '@src/context/store';
import { getMetaContent } from '@tencent/micro-frontend-shared/util';

/**
 * 格式化时间，默认返回时间的年月日
 * @param time 时间
 * @param format 格式化参数
 */
export const formatDate = (time: any, format = 'YYYY-MM-DD') => Moment(time).format(format);

/**
 * 格式化时间，返回时间的年月日，时分秒
 * @param time 时间
 */
export const formatDateTime = (time: any) => formatDate(time, 'YYYY-MM-DD HH:mm:ss');

/**
 * 格式化时间 - xx秒 => xx时xx分xx秒
 * @param second 秒
 */
export const secondToDate = (second: number) => {
  if (second < 0) return '';
  const h = Math.floor(second / 3600);
  const m = Math.floor((second / 60) % 60);
  const s = Math.floor(second % 60);
  return `${h ? `${h} 时 ` : ''}${m ? `${m} 分 ` : ''}${s ? `${s} 秒` : ''}`;
};

/**
 * 根据用户UID获取用户头像url
 * @param uid 用户UID
 */
export function getUserImgUrl(uid: string) {
  return `${LOGIN_SERVER_API}/login/users/${uid}/`;
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

/**
 * 获取当前查询参数
 */
export const getQuery = () => qs.parse(window.location.search.replace('?', ''));

/**
 * 获取项目成员
 */
export const getProjectMembers = () => {
  const { projectMembers } = useStateStore();
  const { admins, users } = projectMembers;

  return uniqBy([...admins, ...users], 'username');
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
 * 重新登录，节流
 */
export const reLogin = throttle((content?: string) => {
  content && message.warning(content);
  const timer = setTimeout(() => {
    window.location.href = `/login?redirect_uri=${encodeURIComponent(window.location.href)}`;
    clearTimeout(timer);
  }, 300);
}, 1000);

export const isEnableManage = () => getMetaContent('ENABLE_MANAGE', process.env.ENABLE_MANAGE) === 'TRUE';

/**
 * 根据代码库地址获取代码库名称
 * @param url - 代码库地址
 * @returns
 */
export const getRepoName = (url: string) => {
  if (isEmpty(url)) {
    return '';
  }
  const urls = url.split('/');
  return urls?.[urls.length - 1];
};
