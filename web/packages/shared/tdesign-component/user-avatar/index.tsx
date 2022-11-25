import React, { useMemo } from 'react';
import { Avatar, AvatarProps } from 'tdesign-react';

import { UserIcon } from 'tdesign-icons-react';

interface UserAvatarProps extends AvatarProps {
  /** 头像昵称 */
  nickname: string;
  /** 头像地址 */
  url?: string;
  /** 仅展示头像 */
  onlyAvatar?: boolean;
  /** 展示头像icon */
  showIcon?: boolean;
}

const COLOR_LIST = [
  {
    color: '#d46b08',
    backgroundColor: '#ffe7ba',
  },
  {
    color: '#d48806',
    backgroundColor: '#fff1b8',
  },
  {
    color: '#7cb305',
    backgroundColor: '#f4ffb8',
  },
  {
    color: '#096dd9',
    backgroundColor: '#bae7ff',
  },
  {
    color: '#c41d7f',
    backgroundColor: '#ffd6e7',
  },
  {
    color: '#531dab',
    backgroundColor: '#efdbff',
  },
];

const UserAvatar = ({ url, nickname, onlyAvatar = false, showIcon = false, ...avatarProps }: UserAvatarProps) => {
  const avatarRender = useMemo(() => {
    if (url) {
      return <Avatar {...avatarProps} image={url} />;
    }
    if (nickname) {
      const colorStyle = COLOR_LIST[nickname.toString().charCodeAt(0) % COLOR_LIST.length];
      return <Avatar {...avatarProps} icon={showIcon ? <UserIcon /> : undefined}
        style={{ ...avatarProps.style, ...colorStyle }} >
        {nickname.toString()[0].toUpperCase()}
      </Avatar>;
    }
    return '';
  }, [nickname, url]);

  return <>
    {avatarRender} {!onlyAvatar && nickname && <span className='mx-xs text-weight-medium vertical-middle inline-block' style={{ color: '#202d40' }}>{nickname}</span>}
  </>;
};
export default UserAvatar;
