// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 公共请求
 */
import { post } from './index';

export const LOGIN_SERVER_API = '/server/credential/api/v3/login';

/**
 * 获取账号密码登录谢谢
 * @param username 用户名
 * @param password 密码
 */
export const postPasswordInfo = (username: string, password: string) => post(`${LOGIN_SERVER_API}/get_oapassword_info/`, { username, password });
