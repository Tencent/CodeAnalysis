import fs from 'fs';

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

/**
 * 修改项目目录下的tsconfig文件，变更文件内的plat地址
 * @param file 文件地址
 * @param platformEnv 所属平台环境变量
 */
export const modTsConfigPaths = (file: string, platformEnv = '') => {
  if (platformEnv) {
    const data = fs.readFileSync(file, 'utf-8');
    // 将tsconfig paths中的 @plat/* 别名替换内容
    const tsconfig = data.replace(/"@plat\/\*":[^\n\r,]*/g, `"@plat/*": ["src/plat/${platformEnv}/*"]`);
    fs.writeFileSync(file, tsconfig, 'utf-8');
  }
};
