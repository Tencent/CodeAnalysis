import React from 'react';
import { FolderOpenIcon } from 'tdesign-icons-react';
import s from './style.scss';

interface EmptyProps {
  icon?: React.ReactNode;
  text?: string;
}

const Empty = ({ icon = <FolderOpenIcon size={24} />, text = '暂无数据' }: EmptyProps) => (
  <div className={s.empty}>
    {icon}
    {text}
  </div>
);

export default Empty;
