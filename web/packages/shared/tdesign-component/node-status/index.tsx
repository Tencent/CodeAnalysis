/**
 * 节点状态组件
 */
import React from 'react';
import { Tag } from 'tdesign-react';
import { LoadingIcon, MinusCircleIcon, ErrorCircleIcon, ChartBubbleIcon } from 'tdesign-icons-react';

export enum StatusEnum {
  /** 不可用 */
  DISACTIVE,
  /** 活跃 */
  ACTIVE,
  /** 离线 */
  OFFLINE,
}

export enum StateEnum {
  /** 空闲 */
  FREE,
  /** 忙碌 */
  BUSY
}


interface NodeStatusProps {
  /** 节点信息 */
  node: any
}

/** 节点状态组件 */
const NodeStatus = ({ node }: NodeStatusProps) => {
  if (node) {
    const { enabled, state } = node;
    if (enabled === StatusEnum.ACTIVE && state === StateEnum.BUSY) {
      return <Tag icon={<LoadingIcon />} theme="primary" variant="light">运行中</Tag>;
    }
    if (enabled === StatusEnum.ACTIVE) {
      return <Tag icon={<ChartBubbleIcon />} theme="success" variant="light">在线</Tag>;
    }
    if (enabled === StatusEnum.DISACTIVE) {
      return <Tag icon={<MinusCircleIcon />}>不可用</Tag>;
    }
    return <Tag icon={<ErrorCircleIcon />} theme="warning" variant="light">离线</Tag>;
  }
  return <></>;
};

export default NodeStatus;
