import React from 'react';

import { useInitMamoto } from './utils/matomo';

interface InitMatomoProps {
  children: React.ReactNode
}

/**
 * 初始化matomo
 */
const InitMatomo = ({ children }: InitMatomoProps) => {
  useInitMamoto();
  return <>{children}</>;
};

export default InitMatomo;
