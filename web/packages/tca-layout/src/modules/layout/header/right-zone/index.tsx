import React from 'react';
import classnames from 'classnames';
import { Dropdown, Avatar } from 'coding-oa-uikit';
// 项目内
import { useStateStore } from '@src/context/store';
import { gUserImgUrl } from '@src/utils';
import s from './style.scss';
import UserMenu from './user-menu';

interface IProps {
  org: any;
}

const RightZone = ({ org }: IProps) => {
  const { userinfo } = useStateStore();

  return (
    <div className={s.rightZone}>
      <Dropdown overlay={UserMenu(userinfo, org)}>
        <div className={s.user}>
          <Avatar
            size="small"
            src={userinfo.avatar_url || gUserImgUrl(userinfo.username)}
            className={s.avatar}
          />
          <span className={classnames(s.angle)} />
        </div>
      </Dropdown>
    </div>
  );
};
export default RightZone;
