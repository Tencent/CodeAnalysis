declare module '*.scss';
declare module '*.svg';

declare const PLATFORM_ENV: 'saas' | 'private' | 'open';

declare const ENABLE_MANAGE: boolean;

/** 列表接口数据结构 */
interface ListAPIDataProps {
  count?: number;
  results?: any[];
  next?: string;
  previous?: string
}
