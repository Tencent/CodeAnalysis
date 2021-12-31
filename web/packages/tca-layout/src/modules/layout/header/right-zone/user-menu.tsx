import React from 'react';
import { Menu, Avatar } from 'coding-oa-uikit';
import { Link } from 'react-router-dom';
import classnames from 'classnames';

// 项目内
import { t } from '@src/i18n/i18next';
import { gUserImgUrl, logout } from '@src/utils';
import { DOC_PATH } from '@src/utils/getRoutePath';
import Language from './language';
import Org from './org';
import s from './style.scss';

const menu = (userinfo: any, org: any) => (
  <Menu>
    <div className={classnames(s.userInfo)}>
      <Avatar
        src={userinfo.avatar_url || gUserImgUrl(userinfo.uid)}
        className={s.userAvatar}
      />
      <div className={s.infoContent}>
        <div className={s.userName} title={userinfo.nickname}>
          {userinfo.nickname}
        </div>
        {/* <div className={s.email} title={user.email}>
                        {user.email}
                    </div> */}
      </div>
    </div>
    <Menu.Item key="user-profile">
      <Link to="/user/profile">{t('个人中心')}</Link>
    </Menu.Item>
    <Menu.Item key="user-auth">
      <Link to="/user/auth">{t('凭证管理')}</Link>
    </Menu.Item>
    <Menu.Item key="user-manage">
      <Link to="/user/manage">{t('用户管理')}</Link>
    </Menu.Item>
    {org.org_sid && (
      <Menu.Item key="org" className={s.orgPopover}>
        <Org org={org} />
      </Menu.Item>
    )}
    <Menu.Item key="languages" className={s.languagePopover}>
      <Language />
    </Menu.Item>
    <Menu.Item key="docs">
      <a href={DOC_PATH} target="_blank" rel="noreferrer">
        {t('帮助文档')}
      </a>
    </Menu.Item>
    <Menu.Item
      key="logout"
      onClick={() => {
        logout(t('退出登录中...'));
      }}
    >
      <div className={classnames(s.logout)}>{t('退出')}</div>
    </Menu.Item>
  </Menu>
);

export default menu;
