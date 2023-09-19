export * from './meta';
export * from './time';
export * from './route';
export * from './size';
export * from './check';
export * from './blob';
export * from './url';
export * from './user';
export { default as LogMgr } from './log';


type CHOICES = {
  [key: number | string]: string
};

/**
 * 将choices转成options
 * @param choices
 * @returns options
 */
export const generateOptions = (choices: CHOICES, isNumber = false) => Object.keys(choices).map(key => ({
  label: choices[key],
  text: choices[key],
  value: isNumber ? parseInt(key, 10) : key,
}));
