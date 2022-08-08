/**
 * 节点状态组件
 */
import React from 'react';
import { Tag } from 'tdesign-react';
import { LoadingIcon, MinusCircleIcon, ErrorCircleIcon, ChartBubbleIcon } from 'tdesign-icons-react';

export const STATUS_ENUM = {
  /** 不可用 */
  DISACTIVE: 0,
  /** 活跃 */
  ACTIVE: 1,
  /** 离线 */
  OFFLINE: 2,
};

export const STATE_ENUM = {
  /** 空闲 */
  FREE: 0,
  /** 忙碌 */
  BUSY: 1,
};


interface NodeStatusProps {
  /** 节点信息 */
  node: any
}

/** 节点状态组件 */
const NodeStatus = ({ node }: NodeStatusProps) => {
  if (node) {
    const { enabled, state } = node;
    if (enabled === STATUS_ENUM.ACTIVE && state === STATE_ENUM.BUSY) {
      return <Tag icon={<LoadingIcon />} theme="primary" variant="light">运行中</Tag>;
    }
    if (enabled === STATUS_ENUM.ACTIVE) {
      return <Tag icon={<ChartBubbleIcon />} theme="success" variant="light">在线</Tag>;
    }
    if (enabled === STATUS_ENUM.DISACTIVE) {
      return <Tag icon={<MinusCircleIcon />}>不可用</Tag>;
    }
    return <Tag icon={<ErrorCircleIcon />} theme="warning" variant="light">离线</Tag>;
  }
  return <></>;
};

export default NodeStatus;
