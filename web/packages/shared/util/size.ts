/**
 * util - size工具库
 */

const sizes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

/**
 * 字节格式转化
 * @param bytes 字节
 * @returns 格式化后字节大小
 */
export const bytesToSize = (bytes: number) => {
  if (typeof bytes !== 'number') {
    return '-';
  }
  if (bytes === 0) return '0 B';
  const k = 1024;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / (k ** i)).toPrecision(3)} ${sizes[i]}`;
};
