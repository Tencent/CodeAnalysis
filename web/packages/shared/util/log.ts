/**
 * utils - log 工具库
 */

/**
 * 打印带有前缀的日志
 * @param prefix 前缀
 * @returns 打印带有前缀的日志
 */
export const prefixLog = (prefix = '') => ({
  info: (message: any, ...optionalParams: any[]) => {
    Log.info(prefix + message, ...optionalParams);
  },
  error: (message: any, ...optionalParams: any[]) => {
    Log.error(prefix + message, ...optionalParams);
  },
  warn: (message: any, ...optionalParams: any[]) => {
    Log.warn(prefix + message, ...optionalParams);
  },
});

/**
 * 日志
 */
const Log = {
  info: (message: any, ...optionalParams: any[]) => {
    console.info(message, ...optionalParams);
  },
  error: (message: any, ...optionalParams: any[]) => {
    console.error(message, ...optionalParams);
  },
  warn: (message: any, ...optionalParams: any[]) => {
    console.warn(message, ...optionalParams);
  },
  prefixLog,
};

export default Log;

