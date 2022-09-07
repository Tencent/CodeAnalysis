import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import classnames from 'classnames';
import { Dropdown, Menu } from 'coding-oa-uikit';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';
import UserAvatar from '@tencent/micro-frontend-shared/component/user-avatar';

// 项目内
import { NAMESPACE, UserState } from '@src/store/user';
import { logout, getNickName } from '@src/utils';
import { isEnableManage, getDocURL } from '@plat/util';
import { getManageRouter, getUserProfileRouter, getUserAuthRouter } from '@src/utils/getRoutePath';
import s from './style.scss';
import Org from './org';
import Language from './language';

interface IProps {
  org: any;
}

const RightZone = ({ org }: IProps) => {
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const { t } = useTranslation();

  const isManage = /^\/manage/.test(window.location.pathname);

  const children = <div className={s.user}>
    <UserAvatar url={userinfo.avatar_url} nickname={getNickName(userinfo)} />
    <span className={classnames(s.angle)} />
  </div>;

  return (
    <div className={s.rightZone}>
      <Dropdown overlay={<Menu>
        <div className={classnames(s.userInfo)}>
          <UserAvatar onlyAvatar url={userinfo.avatar_url} nickname={getNickName(userinfo)} />
          <div className={s.infoContent}>
            <div className={s.userName} title={userinfo.nickname}>
              {userinfo.nickname}
            </div>
          </div>
        </div>
        <Menu.Item key="user-profile">
          <Link to={getUserProfileRouter()}>{t('个人中心')}</Link>
        </Menu.Item>
        <Menu.Item key="user-auth">
          <Link to={getUserAuthRouter()}>{t('凭证管理')}</Link>
        </Menu.Item>
        {false}
        {org.org_sid && (
          <Menu.Item key="org" className={s.orgPopover}>
            <Org name={org.name} />
          </Menu.Item>
        )}
        <Menu.Item key="languages" className={s.languagePopover}>
          <Language />
        </Menu.Item>
        {(isEnableManage() || userinfo?.is_superuser) && !isManage && (
          <Menu.Item key="manage">
            <Link to={getManageRouter()}>{t('管理入口')}</Link>
          </Menu.Item>
        )}
        <Menu.Item key="docs">
          <a href={getDocURL()} target="_blank" rel="noreferrer">
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
      </Menu>}>
        {children}
      </Dropdown>
    </div>
  );
};
export default RightZone;
