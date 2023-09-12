declare module '*.scss';
declare module '*.svg';

declare const ENABLE_MANAGE: string;

/** 列表接口数据结构 */
interface RestfulListAPIParams {
  results: any[];
  count: number;
  next: string;
  previous: string
}
