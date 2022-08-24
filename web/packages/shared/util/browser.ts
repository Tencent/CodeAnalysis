
/**
 * 判断是否企业微信内置浏览器
 * @returns boolean
 */
export const isWxWorkBrowser = () => {
  const ua = navigator.userAgent.toLowerCase();
  const isWx = ua.match(/MicroMessenger/i)?.[0] === 'micromessenger';
  const isWxWork = ua.match(/WxWork/i)?.[0] === 'wxwork';
  return isWx && isWxWork;
};

/**
 * 判断是否微信内置浏览器
 * @returns boolean
 */
export const isWxBrowser = () => {
  const ua = navigator.userAgent.toLowerCase();
  const isWx = ua.match(/MicroMessenger/i)?.[0] === 'micromessenger';
  const isWxWork = ua.match(/WxWork/i)?.[0] === 'wxwork';
  return isWx && !isWxWork;
};

/**
 * 判断是否QQ内置浏览器
 * @returns boolean
 */
export const isQQBrowser = () => {
  const ua = navigator.userAgent.toLowerCase();
  const isQQ = ua.match(/QQ/i)?.[0] === 'qq';
  return isQQ;
};

/**
 * 判断是否支付宝内置浏览器
 * @returns boolean
 */
export const isAlipayBrowser = () => {
  const ua = navigator.userAgent.toLowerCase();
  const isAlipay = ua.match(/AlipayClient/i)?.[0] === 'alipayclient';
  return isAlipay;
};
