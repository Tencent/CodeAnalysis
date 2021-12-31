import { info } from '@src/utils';

const checkBrowser = () => {
  info('校验不支持的浏览器 ...');
  const ua = window.navigator.userAgent.toLowerCase();
  const isIE = ua.indexOf('msie ') > -1 || ua.indexOf('trident/') > -1;
  if (isIE) {
    window.location.href = `/unsupported-browser.html?ref=${encodeURIComponent(window.location.href)}`;
  }
};

export default checkBrowser();
