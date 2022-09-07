import React from 'react';
import { Layout } from 'coding-oa-uikit';

// 项目内
import { FOOTER_DESC } from '@plat/modules/home';
import s from './style.scss';

const Footer = () => (
  <Layout.Footer className={s.footerContainer}>
    <div className={s.footer}>
      <div className="fs18 text-white">
        <p className="mb-xs fs-14">{FOOTER_DESC}</p>
        <p className="mb-xs">Copyright © 1998 - {new Date().getFullYear()} Tencent. All Rights Reserved.</p>
      </div>
    </div>
  </Layout.Footer>
);

export default Footer;
