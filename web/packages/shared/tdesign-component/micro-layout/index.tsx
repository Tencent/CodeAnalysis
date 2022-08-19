import React from 'react';
import { get } from 'lodash';
import Loading from '../loading';
import { useSelector } from 'react-redux';

interface MicroLayoutProps {
  children: React.ReactNode;
  value?: string;
  loading?: React.ReactNode;
  disable?: boolean;
}

const MicroLayout = ({
  children,
  value = 'completed',
  loading = <Loading />,
  disable = false,
}: MicroLayoutProps) => {
  const INITIAL = useSelector((state: any) => state.INITIAL);
  const completed = get(INITIAL, value, false);
  if (!completed && !disable) {
    return <>{loading}</>;
  }
  return <>{children}</>;
};

export default MicroLayout;
