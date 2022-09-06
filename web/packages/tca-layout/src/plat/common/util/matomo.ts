import ReactPiwik from 'react-piwik';

/** 设置 User CustomVariable */
export const setUserInfoCustomVariable = (userinfo: any) => {
  if (userinfo?.nickname) {
    ReactPiwik.push(['setCustomVariable', 1, '用户名', userinfo.nickname, 'visit']);
  }
};
