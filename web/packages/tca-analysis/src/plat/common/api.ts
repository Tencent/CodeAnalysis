import { formatUserAuthAPI, UserAuthAPI } from '@tencent/micro-frontend-shared/tca/user-auth';
import { FetchManager, FetchAPIManager } from '@tencent/micro-frontend-shared/util/fetch';

// 项目内
import { MAIN_SERVER_API } from '@src/constant/api';
import { reLogin } from '@src/utils';

/** 重新定义 fetch manager */
export const fetchManager = new FetchManager({
  headers: {
    Authorization: `CodeDog ${localStorage.getItem('accessToken')}`,
  },
  statusHandler: (response) => {
    if (response.status === 401) {
      reLogin();
    }
  },
});

export const { get, post, put, patch, del, getFile, postFile } = fetchManager;

export const fetchAPIManager = (url: string) => FetchAPIManager.getInstance(url, fetchManager);

/** 用户个人凭证接口 */
export const userAuthAPI: UserAuthAPI = formatUserAuthAPI(
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmsshinfos/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmaccounts/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmauthinfos/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/oauthsettings/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmauthinfo/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/gitcallback/`),
);
