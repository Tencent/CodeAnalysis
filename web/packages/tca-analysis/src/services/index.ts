// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import qs from 'qs';
import { values, isEmpty } from 'lodash';
import { message } from 'coding-oa-uikit';

import fetch from '@src/utils/fetch';
import { reLogin } from '../utils';

export const ERROR_CODE = -1;

function jsonInterceptor(res: any) {
  if (res.status === 401) {
    reLogin('登录失效，请重新登录...');
    return Promise.reject();
  }

  if (res.status === 204) {
    return { code: 0 };
  }

  // 请求成功
  return Promise.resolve(res.json());
}

export function errorInterceptor(json: any) {
  if (!json || JSON.stringify(json) === '{}') {
    return Promise.reject(json);
  }

  if (json.code === 0) {
    return Promise.resolve(json.data);
  }

  if (json.msg) {
    const errors = getErrorMessage(json.msg);
    message.error(errors);
  }

  return Promise.reject(json);
}

function request(url: string, options?: any) {
  return fetch(url, {
    headers: {
      'Content-Type': 'application/json',
    },
    credentials: 'include',
    ...options,
  })
    .then(jsonInterceptor)
    .then(errorInterceptor)
    .catch((err: any) => Promise.reject(err));
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
    body: JSON.stringify(data),
  });
}

export function getFile(url: string, data?: any) {
  return fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json;charset=UTF-8',
    },
    body: data ? JSON.stringify(data) : null,
  }, true)
    .catch((err: any) => Promise.reject(err));
}

export function postFile(url: string, data?: any) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  })
    .then((res) => {
      if (res.status === 200) {
        return Promise.resolve(res);
      } if (res.status === 401) {
        reLogin('登录失效，请重新登录...');
        return Promise.reject();
      }
      return Promise.reject(res.json().then(errorInterceptor));
    })
    .catch((err: any) => Promise.reject(err));
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

function getErrorMessage(msg: any): any {
  if (msg) {
    if (typeof msg === 'string') {
      return msg;
    }

    if (Array.isArray(msg)) {
      const errors = values(msg) || [];
      return errors.pop();
    }

    if (typeof msg === 'object' && Object.keys(msg).length > 0) {
      return getErrorMessage(msg[Object.keys(msg).pop() as any]);
    }
  }

  return '未知错误';
}
