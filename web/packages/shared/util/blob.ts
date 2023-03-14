/**
 * utils - blob 工具库，文件下载相关
 */

/**
 * 触发自动下载
 * @param url 下载链接
 * @param filename 文件名
 */
export const downloadFromUrl = (url: string, filename: string) => {
  const pom = document.createElement('a');
  pom.href = url;
  pom.setAttribute('download', filename);
  pom.click();
};

/**
 * 导出指定内容
 * @param content 下载内容
 * @param filename 文件名
 * @param contentType 文件类型
 */
export const downloadContent = (content: string | ArrayBuffer, filename: string, contentType: string) => {
  const blob = new Blob([content], { type: contentType });
  const url = URL.createObjectURL(blob);

  downloadFromUrl(url, filename);
};
