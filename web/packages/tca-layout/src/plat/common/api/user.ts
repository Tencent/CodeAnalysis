import merge from 'lodash/merge';
import { formatUserAuthAPI, UserAuthAPI } from '@tencent/micro-frontend-shared/tca/user-auth';

// 项目内
import {
  MAIN_SERVER_API,
  LOGIN_SERVER_API,
  fetchAPIManager,
  get, put } from './common';

/** 用户相关API接口 */
export class UserAPI {
  /** 获取用户信息 */
  static getUserInfo() {
    return UserAPI.getUserByLoginProxy();
  }

  /** 更新用户信息 */
  static putUserInfo(data: any) {
    return UserAPI.putUserByLoginProxy(data);
  }

  /** 更新main服务用户信息 */
  protected static putMainUserInfo(params: any) {
    return put(`${MAIN_SERVER_API}/authen/userinfo/`, {
      codedog_user: params,
    });
  }

  /** 从登录服务获取用户信息 */
  private static getUserByLoginProxy() {
    return get(`${LOGIN_SERVER_API}/login/user/`, null, { showError: false })
      .then(response => UserAPI.putMainUserInfo(response).then(result => merge(response, result)))
      .catch(() => get(`${MAIN_SERVER_API}/authen/userinfo/`));
  }

  /** 从登录服务更新用户信息 */
  private static putUserByLoginProxy(data: any) {
    return put(`${LOGIN_SERVER_API}/login/user/`, data, { showError: false }).then(((response) => {
      const newData = merge(response, data);
      return UserAPI.putMainUserInfo(newData).then(result => merge(newData, result));
    }))
      .catch(() => get(`${MAIN_SERVER_API}/authen/userinfo/`));
  }
}

/** 用户个人凭证接口 */
export const userAuthAPI: UserAuthAPI = formatUserAuthAPI(
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmsshinfos/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmaccounts/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmauthinfos/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/oauthsettings/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/scmauthinfo/`),
  fetchAPIManager(`${MAIN_SERVER_API}/authen/gitcallback/`),
);
