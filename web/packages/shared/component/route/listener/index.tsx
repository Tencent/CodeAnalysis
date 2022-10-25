/**
 * 用于父子页面路由监听
 */
import React, { useEffect } from 'react';
import { useHistory, useLocation } from 'react-router-dom';
import { LogMgr } from '../../../util';
/** 跨页面通信消息状态码 */
export enum PostMessageCode {
  SUCCESS = 200,
}

/** 跨页面通信消息数据结构 */
export interface PostMessageData {
  code: number;
  type: string;
  data: string;
}

/** route接收消息数据结构 */
export interface RouteReceiveMessage {
  /** 接受消息来源 */
  eventOrigin?: string;
  /** 接收消息类型 */
  messageType?: string;
  /** history 路由跳转类型  */
  jumpType?: 'push' | 'replace';
  /** 路由前缀，接收路由时会增加路由前缀再执行跳转发送 */
  prefix?: string;
  /** 自定义处理 */
  customHandler?: (event: MessageEvent<PostMessageData>) => void;
}

/** route发送消息数据结构 */
export interface RoutePostMessage {
  /** 自定义操作 */
  customHandler?: (urlPath: string) => void
  /** 发送消息目标源，不存在customHandler时必传 */
  targetOrigin?: string;
  /** 发送消息类型，不存在customHandler时必传 */
  messageType?: string;
  /** 是否处于 iframe 内 */
  inIframe?: boolean;
  /** 路由前缀，发送路由时会替换路由前缀再发送 */
  prefix?: string;
}

interface RouteListenerProps {
  postMessage?: RoutePostMessage;
  receiveMessage?: RouteReceiveMessage;
  children: React.ReactNode;
}

const RouteListener = ({ receiveMessage, postMessage, children }: RouteListenerProps) => {
  const history = useHistory();

  const { pathname, search, hash } = useLocation();
  // 获取url path
  const urlPath = `${pathname}${search}${hash}`;

  useEffect(() => {
    if (postMessage?.customHandler) {
      // 存在自定义操作
      postMessage.customHandler(urlPath);
    } else if (postMessage?.targetOrigin && postMessage.messageType) {
      // 存在目标源以及消息类型
      // 路由变更时发送消息
      const msg: PostMessageData = {
        code: PostMessageCode.SUCCESS,
        type: postMessage.messageType,
        // 存在前缀则先替换前缀
        data: postMessage.prefix ? urlPath.replace(postMessage.prefix, '') : urlPath,
      };
      if (postMessage.inIframe && window.self !== window.top) {
        // 在iframe内，对iframe父页面发送路由变更消息
        window.top?.postMessage(msg, postMessage.targetOrigin);
      } else {
        LogMgr.warn('route 路由变更，未发送消息');
      }
    }
  }, [urlPath, postMessage]);

  useEffect(() => {
    const receiveRouteHandler = (event: MessageEvent<PostMessageData>) => {
      if (receiveMessage?.customHandler) {
        // 存在自定义操作
        receiveMessage.customHandler(event);
      } else if (
        receiveMessage?.eventOrigin && receiveMessage.messageType
        && receiveMessage.jumpType && event.origin === receiveMessage.eventOrigin) {
        // 存在发送源、消息类型、路由调整类型，且来自发送源消息
        const { code, type, data } = event.data;
        if (code === PostMessageCode.SUCCESS && type === receiveMessage.messageType) {
          // 默认匹配
          const urlPath = receiveMessage.prefix ? `${receiveMessage.prefix}${data}` : data;
          history[receiveMessage.jumpType](urlPath);
        } else {
          LogMgr.warn('接收到 route 消息，未匹配成功，未进行任何处理');
        }
      }
    };
    receiveMessage && window.addEventListener('message', receiveRouteHandler, false);
    return () => {
      receiveMessage && window.removeEventListener('message', receiveRouteHandler);
    };
  }, [receiveMessage]);

  return <>{children}</>;
};

export default RouteListener;
