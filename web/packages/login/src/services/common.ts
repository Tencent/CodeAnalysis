/**
 * 公共请求
 */
import { post } from '@tencent/micro-frontend-shared/util/fetch';

export const LOGIN_SERVER_API = '/server/credential/api/v3/login';

/**
 * 获取账号密码登录信息
 * @param username 用户名
 * @param password 密码
 */
export const postPasswordInfo = (username: string, password: string) => post(`${LOGIN_SERVER_API}/get_oapassword_info/`, { username, password });
