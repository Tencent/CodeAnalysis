import { message } from 'coding-oa-uikit';

import { post } from '@plat/api';
import { MAIN_SERVER_API } from '@src/constant/api';

const WINDOW_TMF_APP_INFO_NAME = '_tmfAppInfo';

interface TmfAppInfo {
  orgSid: string;
  teamName: string;
  prefix: string;
}

/** 从Window中立即获取tmfAppInfo */
export const getWindowTmfAppInfo = () => (window as any)[WINDOW_TMF_APP_INFO_NAME] as TmfAppInfo || {
  orgSid: '',
  teamName: '',
  prefix: '',
};

/** 将 tmf app info 载入 window 内 */
const setWindowTmfAppInfo = (orgSid: string, teamName: string) => {
  const tmfAppInfo: TmfAppInfo = {
    orgSid,
    teamName,
    prefix: `/t/${orgSid}/p/${teamName}`,
  };
  // 将获取数据存入window内
  if (!window.hasOwnProperty.call(window, WINDOW_TMF_APP_INFO_NAME)) {
    Object.defineProperty(window, WINDOW_TMF_APP_INFO_NAME, {
      value: tmfAppInfo,
    });
  }
  return tmfAppInfo;
};

/** 绑定tmf应用并获取信息，并存入window */
export const bindTmfApp = () => new Promise<TmfAppInfo>((resolve) => {
  const tmfAppInfo = (window as any)[WINDOW_TMF_APP_INFO_NAME];
  if (tmfAppInfo) {
    resolve(tmfAppInfo);
  } else {
    post(`${MAIN_SERVER_API}/tmf/teams/bind/`, null, { showError: false }).then((res: any) => {
      const orgSid = res.org_sid;
      const teamName = res.name;
      resolve(setWindowTmfAppInfo(orgSid, teamName));
    })
      .catch(() => {
        message.error('应用绑定出现异常，请重试或联系管理员');
      });
  }
});
