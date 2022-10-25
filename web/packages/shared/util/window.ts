/**
 * utils - window窗口操作工具库
 */

/**
 * 计算窗口居中弹出位置
 * @params width 窗口宽度
 * @params height 窗口高度
 */
export const getOpenWindowStyle = (width = 800, height = 800) => {
  const top = window.innerHeight > height ? (window.innerHeight - height) / 2 : 0;
  const left = window.innerWidth > width ? (window.innerWidth - width) / 2 : 0;
  return `top=${top},left=${left},width=${width},height=${height}`;
};

/**
 * 弹出窗口
 * @params url 弹窗地址
 * @params name 弹窗名称
 * @params width 窗口宽度
 * @params height 窗口高度
 */
export const openWindow = (
  /** 要在新打开的窗口中加载的 URL */
  url: string,
  /** 新窗口的名称 */
  name: string,
  /** 新窗口的宽度 */
  width?: number,
  /** 新窗口的高度 */
  height?: number,
) => window.open(url, name, getOpenWindowStyle(width, height));

/** 跨页面通信消息状态码 */
export enum PostMessageCode {
  SUCCESS = 200,
  FAIL = 500,
}

/** 跨页面通信消息类型 */
export enum PostMessageType {
  GIT_OAUTH = 'GitOAuth',
  TAPD_OAUTH = 'TapdOAuth'
}

/** 跨页面通信消息数据结构 */
export interface PostMessageData {
  code: PostMessageCode;
  type: PostMessageType;
  data?: any;
}

/**
 * 跨页面通信
 * @params target 通信对象窗口
 * @params msg 通信消息
 */
export const postMessageToTarget = (target: Window, msg: PostMessageData, targetOrigin?: string) => {
  target.postMessage(msg, targetOrigin || target.location.origin);
};
