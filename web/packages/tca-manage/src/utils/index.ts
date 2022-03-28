/**
 * utils 工具类
 */
import qs from 'qs';
import Moment from 'moment';
import { message } from 'coding-oa-uikit';
import { forEach, pick, get, throttle } from 'lodash';

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

const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

export const bytesToSize = (bytes: number) => {
  if (typeof bytes !== 'number') {
    return '-'
  }
  if (bytes === 0) return '0 B';
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return (bytes / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i];
}

/**
 * 秒转date
 * @param second 秒
 * @returns 格式化后的时间
 */
export const secondToDate = (second: number) => {
  const h = Math.floor(second / 3600);
  const m = Math.floor(((second / 60) % 60));
  const s = Math.floor((second % 60));
  return `${h ? `${h} 时 ` : ''}${m ? `${m} 分 ` : ''}${s ? `${s} 秒` : ''}`;
};

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
export const LOG_PREFIX = '[Micro Frontend Manage] ';

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
 * 是否开启后台管理版本
 */
export const isEnableManage = () => getRuntimeEnv('ENABLE_MANAGE', process.env.ENABLE_MANAGE) === 'TRUE';

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
 * 获取当前路径search查询参数
 */
export const getQuery = () => qs.parse(location.search.replace('?', ''));


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
