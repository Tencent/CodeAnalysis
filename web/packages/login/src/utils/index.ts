
/**
 * 防止url调整漏洞，对回调地址进行校验
 * @param href 回调地址
 * @param validHostNames 域名白名单
 * @returns 回调链接
 */
export const xssRedirectUri = (
  redirectUri: string,
  validHostNames: Array<string> = [window.location.hostname],
) => {
  const a = document.createElement('a');
  a.href = decodeURIComponent(redirectUri) || '';
  // 接下来对hostname进行域名白名单的判断
  if (validHostNames.includes(a.hostname)) {
    return a.href;
  }
  return '';
};
