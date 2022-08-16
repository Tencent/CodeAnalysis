/**
 * 节点状态组件
 */
import React from 'react';
import { Tag } from 'coding-oa-uikit';
import Loading from 'coding-oa-uikit/lib/icon/Loading';
import Stop from 'coding-oa-uikit/lib/icon/Stop';
import ExclamationCircle from 'coding-oa-uikit/lib/icon/ExclamationCircle';
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle';

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
      return <Tag icon={<Loading />} color='processing'>运行中</Tag>;
    }
    if (enabled === STATUS_ENUM.ACTIVE) {
      return <Tag icon={<DotCircle />} color='success'>在线</Tag>;
    }
    if (enabled === STATUS_ENUM.DISACTIVE) {
      return <Tag icon={<Stop />}>不可用</Tag>;
    }
    return <Tag icon={<ExclamationCircle />} color='warning'>离线</Tag>;
  }
  return <></>;
};

export default NodeStatus;
