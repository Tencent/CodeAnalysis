/**
 * utils - check 工具库，用于字段等判断校验
 */

/**
 * 判断字段值是否为true
 * @param value 字段值
 * @param strict 是否严格模式，默认false，即如果value为true字符串也可
 * @returns 返回boolean
 */
export const isTrue = (value: any, strict = false) => {
  if (typeof value === 'string' && !strict) {
    return value.toLowerCase() === 'true';
  }
  return value === true;
};
