// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import Cookies from 'universal-cookie';
import { get } from 'lodash';

const cookies = new Cookies();

export const CSRF_HEADER_NAME = 'X-XSRF-TOKEN';
export const CSRF_COOKIE_NAME = 'XSRF-TOKEN';

export function appendXSRFTokenHeader(headers: object): object {
  const xsrfToken = cookies.get(CSRF_COOKIE_NAME);
  if (!xsrfToken) {
    return headers;
  }
  return {
    ...headers,
    [CSRF_HEADER_NAME]: xsrfToken,
  };
}

export default function fetch(url: string, options: any, absolutePath = false) {
  const contentType = get(options, 'headers.Content-Type');

  let headers: any = {
    // 'API-TYPE': 'coding',
    // 'CODING-PROJECT': get(window.reduxStore.getState(), 'APP.currentProject.id')
  };

  const tk = localStorage.getItem('accessToken');
  if (tk && tk !== 'undefined') {
    headers.Authorization = `CodeDog ${tk}`;
  }

  if (contentType) {
    headers = {
      ...headers,
      'Content-Type': contentType,
    };
  }

  options.headers = appendXSRFTokenHeader(headers);

  return window.fetch(`${absolutePath ? '' : window.location.origin}${url}`, options);
}
