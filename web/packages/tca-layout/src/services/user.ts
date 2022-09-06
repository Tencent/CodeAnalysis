import { MAIN_SERVER_API, fetchAPIManager } from '@plat/api';


export const userTokenAPI = () => {
  const { get, put } = fetchAPIManager(`${MAIN_SERVER_API}/authen/userinfo/token/`);
  return { get, put };
};
