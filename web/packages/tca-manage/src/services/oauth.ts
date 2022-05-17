import { get, post, del } from './index';
import { MAIN_SERVER_API } from './common';

export const getAllSettings = () => get(`${MAIN_SERVER_API}/authen/oauthsettings/`);

export const getOAuthSetting = (scm_platform_name: string) => get(`${MAIN_SERVER_API}/authen/oauthsettings/${scm_platform_name}`);

export const delOAuthSetting = (scm_platform_name: string) => del(`${MAIN_SERVER_API}/authen/oauthsettings/${scm_platform_name}`);

export const postOAuthSetting = (params: any = null) => post(`${MAIN_SERVER_API}/authen/oauthsettings/`, params);