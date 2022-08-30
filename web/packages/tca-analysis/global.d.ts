declare module '*.scss';
declare module '*.svg';

/** 列表接口数据结构 */
interface ListAPIDataProps {
  count?: number;
  results?: any[];
  next?: string;
  previous?: string
}
