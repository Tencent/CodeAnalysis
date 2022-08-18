import { FetchManager, FetchAPIManager } from '@tencent/micro-frontend-shared/util/fetch';

// 项目内
import { reLogin } from '../util';

export const MAIN_SERVER_API = '/server/main/api/v2';

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

export const { get, post, put, patch, del } = fetchManager;

export const fetchAPIManager = (url: string) => FetchAPIManager.getInstance(url, fetchManager);
