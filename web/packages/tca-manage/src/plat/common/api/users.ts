import { MAIN_SERVER_API, fetchAPIManager } from './common';

/** 用户API */
export const userAPI = fetchAPIManager(`${MAIN_SERVER_API}/authen/allusers/`);
