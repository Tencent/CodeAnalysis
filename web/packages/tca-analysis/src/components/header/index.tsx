/**
 * Header 组件
 */

import React from 'react';
import { useHistory } from 'react-router-dom';
// import { isString } from 'lodash';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import style from './style.scss';

interface HeaderProps {
  size?: string;
  link?: string; // 路由返回链接
  title: string | React.ReactNode; // 标题
  description?: string;  // 标题描述
  onBack?: () => void; // 返回
}

const Header = (props: HeaderProps) => {
  const history = useHistory();
  const { link, title, size, description, onBack } = props;

  return (
    <div className={style.header}>
      {(link || onBack) && (
        <span
          className={style.backIcon}
          onClick={() => (onBack ? onBack() : history.push(link))}
        >
          <ArrowLeft />
        </span>
      )}
      <div>
        {
          size === 'small' ? (
            <h4 className={style.smallTitle}>{title}</h4>
          ) : (
            <h2 className={style.title}>{title}</h2>
          )
        }
        {
          description && (
            <span className={style.description}>{description}</span>
          )
        }
      </div>

    </div>
  );
};

export default Header;
