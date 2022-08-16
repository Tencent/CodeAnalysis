/**
 * utils - meta 工具库
 */

/**
 * 根据name获取meta标签content
 * @param key meta name值
 * @param defaultValue
 * @returns meta标签的content
 */
export const getMetaContent = (key: string, defaultValue = '') => {
  const meta = document.querySelector(`meta[name=${key}]`) as HTMLMetaElement;
  return meta ? meta.content : defaultValue;
};
