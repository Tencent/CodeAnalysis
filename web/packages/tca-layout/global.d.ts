declare module '*.scss';
declare module '*.svg';
declare module '*.png';
declare module '*.ico';

declare const ENABLE_MANAGE: string;

interface Window {
  microHook: WindowMicroHook;
}

interface RestfulListAPIParams {
  results: any[];
  count: number;
  next: string;
  previous: string
}
