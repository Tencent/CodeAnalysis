import React, { useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import classnames from 'classnames';
import { Space } from 'tdesign-react';

// 模块内
import s from './style.scss';
import { useMount, useMutationObserver, useUpdateEffect } from 'ahooks';
import LogoDark from './logo-dark.png';
import LogoLight from './logo-light.png';
import LogoBlue from './logo-blue.png';

const LOGO_MAP = {
  dark: LogoDark,
  light: LogoLight,
  blue: LogoBlue,
};

interface HeaderProps {
  leftContent?: React.ReactNode;
  rightContent?: React.ReactNode;
  transparent?: boolean;
  height?: number;
  logoColor?: 'dark' | 'light' | 'blue';
  logoSize?: number;
  linkTo?: string;
}

const Header = ({
  leftContent, rightContent, logoSize, linkTo = '/', transparent = false, height = 48, logoColor = 'dark',
}: HeaderProps) => {
  const [logoName, setLogoName] = useState(logoColor);

  const onSetLogoName = () => {
    if (logoName !== 'blue') {
      if (document.documentElement.getAttribute('theme-mode') === 'dark') {
        setLogoName('light');
      } else {
        setLogoName('dark');
      }
    }
  };

  useMount(onSetLogoName);

  useUpdateEffect(() => {
    setLogoName(logoColor);
  }, [logoColor]);

  useMutationObserver(
    onSetLogoName,
    document.documentElement,
    { attributeFilter: ['theme-mode'] },
  );

  const logoHeight = useMemo(() => {
    const logoHeight = height / 2;
    if (!logoSize || logoSize > logoHeight) {
      return logoHeight;
    }
    return logoSize;
  }, [logoSize, height]);

  return <header style={{ height }} className={classnames(s.layoutHeader, transparent ? `${s.layoutHeaderTransparent}` : '')}>
    <Space className={s.leftContent} align='center'>
      <Link to={linkTo}>
        <img height={logoHeight} src={LOGO_MAP[logoName]} />
      </Link>
      {leftContent}
    </Space>
    <Space className={s.rightContent}>
      {rightContent}
    </Space>
  </header>;
};

export default Header;
