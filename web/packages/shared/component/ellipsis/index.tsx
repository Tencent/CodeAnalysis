import React from 'react';
import classnames from 'classnames';

interface IProps {
  maxWidth?: number;
  className?: string;
  children?: React.ReactNode;
}

const EllipsisTemplate = ({ maxWidth, className, children }: IProps) => (
  <div
    className={classnames('ellipsis', className)}
    style={{ maxWidth: `${maxWidth || 300}px` }}
  >
    {children}
  </div>
);

export default EllipsisTemplate;
