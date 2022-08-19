import { MAIN_SERVER_API, fetchAPIManager } from '@plat/api';

export const oauthSettingAPI = fetchAPIManager(`${MAIN_SERVER_API}/authen/oauthsettings/`);
