import merge from 'lodash/merge';
import { get, put, post, del, customRequest } from './index';

import { MAIN_SERVER_API, LOGIN_SERVER_API } from './common';

/**
 * 更新用户信息
 * @param {*} params 参数
 */
export function putUserInfo(params: any) {
  return put(`${MAIN_SERVER_API}/authen/userinfo/`, {
    codedog_user: params,
  });
}

/**
 * 更新用户信息
 * @param params 参数
 */
export const putLoginUserInfo = (params: any) => put(`${LOGIN_SERVER_API}/login/user/`, params)
  .then((response) => {
    const newData = merge(response, params);
    return putUserInfo(newData).then(result => merge(newData, result));
  })
  .catch(() => get(`${MAIN_SERVER_API}/authen/userinfo/`));

export const getUserByLoginProxy = (params: any = {}) => get(`${LOGIN_SERVER_API}/login/user/`)
  .then((response) => {
    const newData = merge(response, params);
    return putUserInfo(newData).then(result => merge(newData, result));
  })
  .catch(() => get(`${MAIN_SERVER_API}/authen/userinfo/`));

export const getUserBySmartProxy = (params: any = {}) => customRequest('/ts:auth/tauth/info.ashx', {
  method: 'POST',
})
  .then((response) => {
    const newData = merge(
      {
        nickname: response.EngName,
        chinese_name: response.ChnName,
      },
      params,
    );
    return putUserInfo(newData);
  })
  .catch(() => get(`${MAIN_SERVER_API}/authen/userinfo/`));

/**
 * 获取用户信息
 */
export const gUserInfo = (params: any = {}) => getUserByLoginProxy(params);

/**
 * 获取用户http凭证
 */
export function gScmAccounts() {
  return get(`${MAIN_SERVER_API}/authen/scmaccounts/`, {
    limit: 200,
  });
}

/**
 * 创建http凭证
 * @param params 参数
 */
export function postScmAccounts(params: any) {
  return post(`${MAIN_SERVER_API}/authen/scmaccounts/`, params);
}

/**
 * 更新http凭证
 * @param id 凭证ID
 * @param params 参数
 */
export function putScmAccount(id: number | string, params: any) {
  return put(`${MAIN_SERVER_API}/authen/scmaccounts/${id}/`, params);
}

/**
 * 删除http凭证
 * @param id 凭证ID
 */
export function delScmAccount(id: number | string) {
  return del(`${MAIN_SERVER_API}/authen/scmaccounts/${id}/`);
}

/**
 * 获取SSH凭证
 */
export const getSSHInfo = () => get(`${MAIN_SERVER_API}/authen/scmsshinfos/`, {
  limit: 200,
});

/**
 * 添加SSH凭证
 * @param data
 */
export const addSSHInfo = (data: any) => post(`${MAIN_SERVER_API}/authen/scmsshinfos/`, data);

/**
 * 更新SSH凭证
 * @param id
 * @param data
 */
export const updateSSHInfo = (id: number, data: any) => put(`${MAIN_SERVER_API}/authen/scmsshinfos/${id}/`, data);

/**
 * 移除SSH凭证
 * @param id
 */
export const delSSHInfo = (id: number) => del(`${MAIN_SERVER_API}/authen/scmsshinfos/${id}/`);

/**
 * 获取用户审批权限结果接口
 */
export const gMinePerm = () => customRequest(`${MAIN_SERVER_API}/authen/perms/mine/`, { method: 'GET' });

/**
 * 变更更新用户审批
 * @param data
 */
export const putMinePerm = (data: any) => put(`${MAIN_SERVER_API}/authen/perms/mine/`, data);

/**
 * 创建审批单
 * @param data 参数
 */
export const postPerm = (data: any) => post(`${MAIN_SERVER_API}/authen/perms/create/`, data);


/**
 * 获取用户token
 */
export const getUserToken = () => get(`${MAIN_SERVER_API}/authen/userinfo/token/`);

/**
 * 刷新用户token
 */
export const putUserToken = () => put(`${MAIN_SERVER_API}/authen/userinfo/token/`, null);
