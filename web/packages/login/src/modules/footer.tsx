import React from 'react';

// 项目内
import s from '../style.scss';


const Footer = () => (
  <footer className={s.footer}>
    <p className="fs18">Copyright © 1998 - {new Date().getFullYear()} Tencent. All Rights Reserved.</p>
  </footer>
);

export default Footer;
