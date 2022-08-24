import merge from 'lodash/merge';

// 项目内
import {
  MAIN_SERVER_API,
  LOGIN_SERVER_API,
  fetchAPIManager,
  get, put, del,
} from './common';

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

  /** 用户http凭证接口 */
  static authAccount() {
    return fetchAPIManager(`${MAIN_SERVER_API}/authen/scmaccounts/`);
  }

  /** 用户ssh凭证接口 */
  static authSSH() {
    return fetchAPIManager(`${MAIN_SERVER_API}/authen/scmsshinfos/`);
  }

  /** 查询OAuth授权配置状况 */
  static getPlatformStatus(param: any = null) {
    return get(`${MAIN_SERVER_API}/authen/oauthsettings/`, param);
  }

  /** 获取用户oauth凭证接口 */
  static getOAuthStatus(param: any = null) {
    return get(`${MAIN_SERVER_API}/authen/scmauthinfo/`, param);
  }

  /** 删除用户oauth凭证接口 */
  static delOAuthStatus(param: any = null) {
    return del(`${MAIN_SERVER_API}/authen/scmauthinfo/`, param);
  }

  /** 获取用户oauth凭证接口 */
  static getOAuthInfos() {
    return get(`${MAIN_SERVER_API}/authen/scmauthinfos/`);
  }

  /** 用户oauth授权接口 */
  static getOAuthCallback(scm_platform_name: string, param: any = {}) {
    return get(`${MAIN_SERVER_API}/authen/gitcallback/${scm_platform_name}/`, param);
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
