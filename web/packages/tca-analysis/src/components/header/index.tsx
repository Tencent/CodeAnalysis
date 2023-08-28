/**
 * Header 组件
 */

import React from 'react';
import { useHistory } from 'react-router-dom';
import { ArrowLeftIcon } from 'tdesign-icons-react';

import style from './style.scss';

interface HeaderProps {
  size?: string;
  link?: string; // 路由返回链接
  title: string | React.ReactNode; // 标题
  description?: string;  // 标题描述
  onBack?: () => void; // 返回
  extraContent?: React.ReactNode; // 按钮等额外内容
}

const Header = (props: HeaderProps) => {
  const history = useHistory();
  const { link, title, size, description, onBack, extraContent } = props;

  return (
    <div className={style.header}>
      {(link || onBack) && (
        <span
          className={style.backIcon}
          onClick={() => (onBack ? onBack() : history.push(link))}
        >
          <ArrowLeftIcon />
        </span>
      )}
      <div style={{ flex: 1 }}>
        {
          size === 'small' ? (
            <h4 className={style.smallTitle}>{title}</h4>
          ) : (
            <h2 className={style.title}>{title}</h2>
          )
        }
        {
          description && (
            <div className={style.description}>{description}</div>
          )
        }
      </div>
      {extraContent}
    </div>
  );
};

export default Header;
