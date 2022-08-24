/**
 * 节点状态组件
 */
import React from 'react';
import { useTranslation } from 'react-i18next';
import { Tag } from 'coding-oa-uikit';
import Loading from 'coding-oa-uikit/lib/icon/Loading';
import Stop from 'coding-oa-uikit/lib/icon/Stop';
import ExclamationCircle from 'coding-oa-uikit/lib/icon/ExclamationCircle';
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle';

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
  const { t } = useTranslation();

  if (node) {
    const { enabled, state } = node;
    if (enabled === StatusEnum.ACTIVE && state === StateEnum.BUSY) {
      return <Tag icon={<Loading />} color='processing'>{t('运行中')}</Tag>;
    }
    if (enabled === StatusEnum.ACTIVE) {
      return <Tag icon={<DotCircle />} color='success'>{t('在线')}</Tag>;
    }
    if (enabled === StatusEnum.DISACTIVE) {
      return <Tag icon={<Stop />}>{t('失效')}</Tag>;
    }
    return <Tag icon={<ExclamationCircle />} color='warning'>{t('离线')}</Tag>;
  }
  return <></>;
};

export default NodeStatus;
