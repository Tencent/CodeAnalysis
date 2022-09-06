import React from 'react';
import { Link } from 'react-router-dom';
import classnames from 'classnames';
import { Space } from 'coding-oa-uikit';

// 模块内
import LogoIco from '@src/images/favicon.ico';
import s from './style.scss';


interface HeaderProps {
  leftContent?: React.ReactNode;
  rightContent?: React.ReactNode;
}

const Header = ({ leftContent, rightContent }: HeaderProps) => (
  <header className={classnames(s.layoutHeader)}>
    <Space className={s.leftContent}>
      <Link to='/'>
        <Space>
          <img width={30} src={LogoIco} />
          <strong className='text-grey-8 inline-block vertical-middle' >腾讯云代码分析</strong>
        </Space>
      </Link>
      {leftContent}
    </Space>
    <Space className={s.rightContent}>
      {rightContent}
    </Space>
  </header>
);

export default Header;
