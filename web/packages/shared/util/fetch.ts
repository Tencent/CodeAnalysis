/**
 * utils - fetch 工具库
 */
import qs from 'qs';
import message from 'coding-oa-uikit/lib/message';

export interface FetchCustomParams {
  /** fetch 自定义headers */
  headers?: HeadersInit;
  /** fetch超时时间，默认30s */
  timeout?: number;
  /** fetch是否提示错误信息，默认展示 */
  showError?: boolean;
  /** fetch 成功处理 */
  resultHandler?: (data: any) => any;
  /** fetch 失败处理，用于处理失败结果 */
  failResultHandler?: (data: any) => any;
  /** fetch 请求状态处理 */
  statusHandler?: (response: Response) => void;
  /** fetch 文件下载处理 */
  fileHandler?: (response: Response) => any;
  // message plugin
  messagePlugin?: any;
}

interface RequestCustom extends FetchCustomParams {
  /** fetch请求是否已收到响应 */
  isFetched: boolean;
  /** fetch请求是否已被中断 */
  isAbort: boolean;
}

/**
 * 封装后的fetch
 * @param input RequestInfo
 * @param init RequestInit
 * @param customParams 自定义请求参数
 * @returns fetch Promise
 */
export const fetch = (input: RequestInfo, init?: RequestInit, customParams?: FetchCustomParams) => {
  // 默认参数
  const defaultCustom: RequestCustom = {
    showError: true,
    headers: {},
    timeout: 30,
    isAbort: false,
    isFetched: false,
  };
  const custom: RequestCustom = Object.assign({}, defaultCustom, customParams);
  if (init) {
    init.headers = Object.assign({}, init.headers, {
      'X-Requested-With': 'XMLHttpRequest',
      'Content-Type': 'application/json;charset=UTF-8',
    });
    // 处理自定义请求头
    if ('headers' in custom) {
      const { headers } = custom;
      init.headers = Object.assign({}, init.headers, headers);
    }
  }
  const fetchPromise = new Promise((resolve, reject) => {
    window.fetch(input, init).then((response) => {
      // 如果请求被中断，则return
      if (custom.isAbort) {
        return;
      }
      // 请求结束，将isFetched置为true
      custom.isFetched = true;
      // 请求状态前置处理
      custom.statusHandler?.(response);
      if (response.status === 204) {
        return resolve({ code: 0 });
      }
      if (response.status === 401) {
        return reject(failResultHandler({ msg: '登录态已过期，重新登录系统！' }, custom));
      }
      // if (response.status === 404) {
      //   return reject(failResultHandler({ msg: '接口不存在' }, custom));
      // }
      // 文件下载自定义结果处理
      if (custom.fileHandler) {
        return resolve(custom.fileHandler(response));
      }
      response.json().then((jsonData) => {
        if (response.ok) {
          return resolve(resultHandler(jsonData, custom));
        }
        return reject(failResultHandler(jsonData, custom));
      })
        .catch(e => reject(failResultHandler(e, custom)));
    })
      .catch((e) => {
        if (custom.isAbort) {
          return;
        }
        custom.isFetched = true;
        return reject(failResultHandler(e, custom));
      });
  });
  // Promise.race 谁先结束就返回哪个数据
  return Promise.race([fetchPromise, fetchTimeout(custom)]);
};

/**
 * fetch超时处理，默认30秒
 * @param custom 自定义request参数
 * @returns Promise
 */
const fetchTimeout = (custom: RequestCustom) => new Promise((resolve, reject) => {
  const timer = setTimeout(() => {
    clearTimeout(timer);
    // 如果还未收到响应结果，则执行超时逻辑，中断结果
    if (!custom.isFetched) {
      // 还未收到响应，则开始超时逻辑，并标记fetch需要放弃
      custom.isAbort = true;
      custom.showError && (custom.messagePlugin || message).error('网络开小差了，稍后再试');
      reject({ msg: 'timeout' });
    }
  }, (custom.timeout || 30) * 1000);
});

/**
 *处理成功结果
 * @param jsonData 请求数据结果
 * @returns 格式化响应数据结果
 */
const resultHandler = (jsonData: any, custom: RequestCustom) => {
  // 自定义成功结果处理
  if (custom.resultHandler) {
    return custom.resultHandler(jsonData);
  }
  return jsonData.data;
};

/**
 * 处理失败结果
 * @param jsonData fetch响应结果
 * @param custom 自定义请求参数
 * @returns 失败响应数据结果
 */
const failResultHandler = (jsonData: any, custom: RequestCustom) => {
  // 自定义失败结果处理
  let { msg } = jsonData;
  if (custom.failResultHandler) {
    msg = custom.failResultHandler(jsonData);
  }
  if (msg && custom.showError) {
    (custom.messagePlugin || message).error(getFailMessage(msg));
  }
  return jsonData;
};

/**
 * 获取失败信息
 * @param msg 信息
 * @returns 返回错误信息
 */
export const getFailMessage: any = (msg: any) => {
  if (msg) {
    if (typeof msg === 'string') {
      return msg;
    }
    if (Array.isArray(msg)) {
      return getFailMessage(msg.pop());
    }
    if (typeof msg === 'object' && Object.keys(msg).length > 0) {
      // 遍历 object
      return getFailMessage(Object.values(msg)?.pop());
    }
  }
  return '接口请求失败';
};

/**
 * GET 方法下载文件结果处理
 * @param response
 * @returns
 */
const getFileResultHandler = (response: Response) => response;

/**
 * POST 方法下载文件结果处理
 * @param response
 */
const postFileResultHandler = (response: Response) => {
  if (response.ok) {
    return Promise.resolve(response);
  }
  return Promise.reject();
};

/** fetch 请求管理模块 */
export class FetchManager {
  private custom?: FetchCustomParams;
  constructor(customParams?: FetchCustomParams) {
    this.custom = customParams;
  }

  get = (url: string, data?: any, custom?: FetchCustomParams) => fetch(`${url}${!data ? '' : `?${qs.stringify(data, { arrayFormat: 'comma' })}`}`, {
    method: 'GET',
  }, { ...this.custom, ...custom });

  post = (url: string, data?: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : null,
  }, { ...this.custom, ...custom });

  put = (url: string, data: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  }, { ...this.custom, ...custom });

  patch = (url: string, data: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'PATCH',
    body: JSON.stringify(data),
  }, { ...this.custom, ...custom });

  del = (url: string, data?: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'DELETE',
    body: data && JSON.stringify(data),
  }, { ...this.custom, ...custom });

  getFile = (url: string, data?: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'GET',
    body: data ? JSON.stringify(data) : null,
  }, {
    fileHandler: getFileResultHandler,
    ...this.custom,
    ...custom,
  });

  postFile = (url: string, data?: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : null,
  }, {
    fileHandler: postFileResultHandler,
    ...this.custom,
    ...custom,
  });

  upload = (url: string, data: any, custom?: FetchCustomParams) => fetch(url, {
    method: 'POST',
    body: data,
  }, { ...this.custom, ...custom });
}

/** 初始化默认的fetch模块 */
export const fetchManager = new FetchManager();

export const { get, post, put, patch, del, getFile, postFile } = fetchManager;

/**
 * 初始化API URL 提供 restful api
 * 单例模式
 */
export class FetchAPIManager {
  private static instance: FetchAPIManager;

  /**
   * 获取 FetchAPIManager 实例
   * @param url API URL
   * @param fm fetchManager
   * @returns FetchAPIManager实例
   */
  static getInstance(url: string, fm = fetchManager) {
    if (!FetchAPIManager.instance || FetchAPIManager.instance.url !== url) {
      FetchAPIManager.instance = new FetchAPIManager(url, fm);
    }
    return FetchAPIManager.instance;
  }

  private url: string;
  private fm: FetchManager;

  constructor(url: string, fm = fetchManager) {
    this.url = url.charAt(url.length - 1) === '/' ? url : `${url}/`;
    this.fm = fm;
  }

  /**
   * 获取实例列表
   * @param data 筛选参数
   * @param custom FetchCustomParams
   * @returns Promise
   */
  get = (data?: any, custom?: FetchCustomParams) => this.fm.get(this.url, data, custom);

  /**
   * 创建实例
   * @param data 数据
   * @param custom FetchCustomParams
   * @returns Promise
   */
  create = (data: any, custom?: FetchCustomParams) => this.fm.post(this.url, data, custom);

  /**
   * 获取实例详情
   * @param id 实例ID
   * @param data 参数
   * @param custom FetchCustomParams
   * @returns Promise
   */
  getDetail = (id: number | string, data?: any, custom?: FetchCustomParams) => this.fm.get(`${this.url}${id}/`, data, custom);

  /**
   * 更新实例
   * @param id 实例ID
   * @param data 更新数据
   * @param custom FetchCustomParams
   * @returns Promise
   */
  update = (id: number | string, data: any, custom?: FetchCustomParams) => this.fm.put(`${this.url}${id}/`, data, custom);

  /**
   * 删除实例
   * @param id 实例ID
   * @param data 数据
   * @param custom FetchCustomParams
   * @returns Promise
   */
  delete = (id: number | string, data?: any, custom?: FetchCustomParams) => this.fm.del(`${this.url}${id}/`, data, custom);

  /**
   * post 操作
   * @param data 参数
   * @param custom FetchCustomParams
   * @returns Promise
   */
  post = (data: any, custom?: FetchCustomParams) => this.fm.post(this.url, data, custom);

  /**
   * put 操作
   * @param data 数据
   * @param extraUrl 额外URL
   * @param custom FetchCustomParams
   * @returns Promise
   */
  put = (data: any, extraUrl = '', custom?: FetchCustomParams) => this.fm.put(`${this.url}${extraUrl}/`, data, custom);

  /**
  * del 操作
  * @param data 数据
  * @param extraUrl 额外URL
  * @param custom FetchCustomParams
  * @returns Promise
  */
  del = (data?: any, extraUrl = '', custom?: FetchCustomParams) => this.fm.del(`${this.url}${extraUrl}/`, data, custom);
}
