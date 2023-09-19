/** 组件状态 */
import React, { FC } from 'react';
import Loading from '../loading';
import Page404 from '../../component/404';
import Page403 from '../../component/403';

export enum ComponentStatusEnum {
  /** 组件加载中 */
  LOADING,
  /** 组件加载完毕 */
  FINISHED,
  /** 组件未找到 */
  NOT_FOUND,
  /** 组织无权限访问 */
  NOT_PERM,
}

interface ComponentStatusProps {
  children: React.ReactElement
  status: ComponentStatusEnum
}

const ComponentStatus: FC<ComponentStatusProps> = ({ status, children }) => {
  if (status === ComponentStatusEnum.FINISHED) {
    return children;
  }
  if (status === ComponentStatusEnum.NOT_FOUND) {
    return <Page404 />;
  }
  if (status === ComponentStatusEnum.NOT_PERM) {
    return <Page403 />;
  }
  return <Loading />;
};

export default ComponentStatus;
