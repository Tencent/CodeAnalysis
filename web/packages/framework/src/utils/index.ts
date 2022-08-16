import isEmpty from 'lodash/isEmpty';

import Constant from '@src/constant';


/**
 * 创建body子集容器
 * @param id dom 节点ID
 * @returns container
 */
export function getOrCreateBodyContainer(id: string): HTMLElement {
  const ele = document.getElementById(id);
  if (ele?.parentNode.isEqualNode(document.body)) {
    return ele;
  }
  ele?.remove();
  const container = document.createElement('div');
  container.id = id;
  document.body.appendChild(container);
  return container;
}

/**
 *  判断是否是 Promise 类型
 * @param promise
 * @return Boolean
 */
export function isPromise(promise: any): boolean {
  return promise && typeof promise.then === 'function' && typeof promise.catch === 'function';
}

type FuncOrPromise = (props?: any) => any | Promise<any>;

export const toPromise = (func?: FuncOrPromise) => (props: any) => {
  if (typeof func !== 'function') {
    return Promise.resolve();
  }

  return isPromise(func) ? ((func as unknown) as Promise<any>) : Promise.resolve(func(props));
};

/**
 * 获取数组或将对象转成数组
 * @param array array or object
 * @return Array
 */
export function toArray<T>(array: T | T[]): T[] {
  return Array.isArray(array) ? array : [array];
}

/**
 * 获取meta标签content
 * @param key
 * @param defaultValue
 */
export const getMetaEnv = (key: string, defaultValue = '') => {
  const meta = document.querySelector(`meta[name=${key}]`) as HTMLMetaElement;
  return meta && !isEmpty(meta.content) ? meta.content : defaultValue;
};

/**
 * 获取LocalStorage name对应值
 * @param name key
 * @param defaultValue 默认🈯️
 */
export function getLocalStorage(name: string, defaultValue = ''): string {
  if (window.localStorage) {
    const value = window.localStorage.getItem(name);
    if (value) {
      return value;
    }
  }
  return defaultValue;
}

/**
 * 设置LocalStorage name对应值
 * @param name key
 * @param value value
 */
export function setLocalStorage(name: string, value = '') {
  if (window.localStorage) {
    window.localStorage.setItem(name, value);
  }
}

/**
 * 移除LocalStorage对应name
 * @param name key
 */
export function cleanLocalStorage(name: string) {
  if (window.localStorage) {
    window.localStorage.removeItem(name);
  }
}

/**
 * 判断LOG_LEVEL是否为DEBUG
 */
export const LOG_DEBUG = getMetaEnv(Constant.LOG_LEVEL) === 'DEBUG';

/**
 * 日志前缀
 */
export const LOG_PREFIX = '[Micro Frontend Framework] ';

/**
 * 如果开启了DEBUG模式才会启用console.debug
 * @param message 信息
 * @param optionalParams 其他参数
 */
export const debug = (message?: any, ...optionalParams: any[]) => {
  if (LOG_DEBUG) {
    console.debug(LOG_PREFIX + message, ...optionalParams);
  }
};

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
  console.error(LOG_PREFIX + message, ...optionalParams);
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
 * 判断字段值是否为true
 * @param value 字段值
 * @param strict 是否严格模式，默认false，即如果value为true字符串也可
 * @returns 返回boolean
 */
export const isTrue = (value: any, strict = false) => {
  if (typeof value === 'string' && !strict) {
    return value.toLowerCase() === 'true';
  }
  return value === true;
};
