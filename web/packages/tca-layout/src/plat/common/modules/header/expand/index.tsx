import React, { FC } from 'react';
export { default as User } from './user';

/** 路由权限控制器 */
export const MessageInterceptor = <P extends object>(Component: FC<P>) => {
  /** HOC */
  const ComponentInject = () => <Component enable={false} />;

  return ComponentInject;
};
