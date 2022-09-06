import { FetchManager, FetchAPIManager } from '@tencent/micro-frontend-shared/util/fetch';

// 项目内
import { reLogin } from '@src/utils';

export const MAIN_SERVER_API = '/server/main/api/v3';
export const ANALYSIS_SERVER_API = '/server/analysis/api/v3';
export const ANALYSIS_SERVER_CODEDOG_API = '/api/codedog/analysis/v3/';
export const LOGIN_SERVER_API = '/server/credential/api/v3';

/** 重新定义 fetch manager */
const fetchManager = new FetchManager({
  headers: {
    Authorization: `CodeDog ${localStorage.getItem('accessToken')}`,
  },
  statusHandler: (response) => {
    if (response.status === 401) {
      reLogin('登录态已过期，重新登录...');
    }
  },
});

export const { get, post, put, patch, del, getFile } = fetchManager;

export const fetchAPIManager = (url: string) => FetchAPIManager.getInstance(url, fetchManager);
