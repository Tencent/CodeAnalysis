import React, { useMemo } from 'react';
import { useSelector } from 'react-redux';
import { useHistory, useParams } from 'react-router-dom';
import { Dropdown } from 'tdesign-react';
import {
  ChevronDownIcon,
  UserCircleIcon,
  PoweroffIcon,
  SecuredIcon,
  DesktopIcon,
} from 'tdesign-icons-react';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';
import UserAvatar from '@tencent/micro-frontend-shared/tdesign-component/user-avatar';

import { isEnableManage } from '@plat/util';
import { t } from '@src/utils/i18n';
import { getManageRouter, getUserProfileRouter, getUserAuthRouter } from '@src/utils/getRoutePath';
import { NAMESPACE, UserState } from '@src/store/user';
import { logout, getNickName } from '@src/utils';
import Org from './org';
import Langauge from '../right-zone/language';

import s from '../style.scss';

const { DropdownMenu, DropdownItem } = Dropdown;

const User = () => {
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const history = useHistory();
  const org = useSelector((state: any) => state.APP)?.org ?? {};
  const { orgSid }: any = useParams();
  const showOrg = org.org_sid && org.org_sid === orgSid;

  /** 是否展示管理后台入口 */
  const showManage = useMemo(() => {
    const isManagePage = /^\/manage/.test(window.location.pathname);
    if (isManagePage) {
      return false;
    }
    return isEnableManage() || userinfo?.is_superuser;
  }, [userinfo?.is_superuser]);

  return <Dropdown className={s.headerDropdown} minColumnWidth={200} direction='left'>
    <div className={s.headerUser}>
      <UserAvatar url={userinfo.avatar_url} nickname={getNickName(userinfo)} />
      <ChevronDownIcon />
    </div>
    <DropdownMenu>
      <DropdownItem onClick={() => {
        history.push(getUserProfileRouter());
      }}>
        <div className={s.headerDropItem}>
          <UserCircleIcon className={s.icon} />
          <span>{t('个人中心')}</span>
        </div>
      </DropdownItem>
      <DropdownItem onClick={() => {
        history.push(getUserAuthRouter());
      }}>
        <div className={s.headerDropItem}>
          <SecuredIcon className={s.icon} />
          <span>{t('凭证管理')}</span>
        </div>
      </DropdownItem>
      {showOrg && <DropdownItem>
        <Org />
      </DropdownItem>}
      <DropdownItem>
        <Langauge />
      </DropdownItem>
      {showManage && <DropdownItem onClick={() => {
        history.push(getManageRouter());
      }}>
        <div className={s.headerDropItem}>
          <DesktopIcon className={s.icon} />
          <span>{t('后台管理')}</span>
        </div>

      </DropdownItem>}
      <DropdownItem onClick={() => {
        logout(t('退出登录中...'));
      }}>
        <div className={s.headerDropItem}>
          <PoweroffIcon className={s.icon} />
          <span>{t('退出登录')}</span>
        </div>
      </DropdownItem>
    </DropdownMenu>
  </Dropdown>;
};

export default User;
