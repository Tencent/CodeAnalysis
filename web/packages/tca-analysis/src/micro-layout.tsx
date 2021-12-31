import React, { ReactNode } from 'react';
import { get } from 'lodash';
import Loading from '@src/components/loading';
import { useSelector } from 'react-redux';

interface IProps {
  children: ReactNode;
  value?: string;
  loading?: ReactNode;
  // 禁用，用于控制 MicroLayout 是否禁用，前期暂时没有layout微前端
  disable?: boolean;
}

const MicroLayout = ({
  children,
  value = 'completed',
  loading = <Loading />,
  disable = false,
}: IProps) => {
  const INITIAL = useSelector((state: any) => state.INITIAL);
  const completed = get(INITIAL, value, false);
  if (!completed && !disable) {
    return <>{loading}</>;
  }
  return <>{children}</>;
};

export default MicroLayout;
