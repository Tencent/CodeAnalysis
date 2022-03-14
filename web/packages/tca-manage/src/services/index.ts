import NProgress from 'nprogress';
import { isEmpty } from 'lodash';
import qs from 'qs';
import { message } from 'coding-oa-uikit';

// import { t } from '@src/i18n/i18next';
import fetch from '../utils/fetch';
// import { reLogin } from '../utils';

function jsonInterceptor(res: any) {
  if (res.status === 401) {
    // reLogin(t('登录失效，请重新登录...'));
    return Promise.reject();
  }

  // 请求成功
  return Promise.resolve(res.status === 204 ? { code: 0 } : res.json());
}

export function errorInterceptor(json: any) {
  if (!json || JSON.stringify(json) === '{}') {
    return Promise.reject(json);
  }
  // 请求成功
  if (json.code === 0) {
    return Promise.resolve(json.data);
  }
  // 临时解决方案，对login服务额外处理，后续需要调整登录服务请求，保证统一
  if (json.status === 200 && json.message === 'success') {
    return Promise.resolve(json);
  }
  // 否则请求失败，失败提示
  message.error(json.msg);
  return Promise.reject(json);
}

function request(url: string, options?: any) {
  NProgress.start();
  return fetch(url, {
    ...options,
    credentials: 'include',
  })
    .then(jsonInterceptor)
    .then(errorInterceptor)
    .catch((err: any) => Promise.reject(err))
    .finally(() => {
      NProgress.done();
    });
}

/**
 * 用于自定义处理fetch结果的接口
 * @param url
 * @param options
 */
export function customRequest(url: string, options?: any) {
  return fetch(url, {
    ...options,
    credentials: 'include',
  }).then(jsonInterceptor);
}

export function get(url: string, data?: any) {
  return request(`${url}${isEmpty(data) ? '' : `?${qs.stringify(data)}`}`, {
    method: 'GET',
  });
}

export function post(url: string, data: any) {
  return request(url, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function put(url: string, data: any) {
  return request(url, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export function del(url: string, data?: any) {
  return request(url, {
    method: 'DELETE',
    body: data && JSON.stringify(data),
  });
}

export function getFilePost(url: string, data: any) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  }).catch((err: any) => Promise.reject(err));
}

export function upload(url: string, data: any) {
  return fetch(url, {
    method: 'POST',
    headers: {},
    body: data,
  })
    .then(jsonInterceptor)
    .catch((err: any) => Promise.reject(err));
}
