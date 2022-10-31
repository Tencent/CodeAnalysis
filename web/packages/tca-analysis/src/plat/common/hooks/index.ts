import { useMemo } from 'react';
import { get } from 'lodash';
import { useSelector } from 'react-redux';

/** 判断登录用户是否是管理员 hook */
export const useLoginUserIsAdmin = (usernames: string[]) => {
  // 判断是否有权限删除分析项目
  const APP = useSelector((state: any) => state.APP);
  const isSuperuser = get(APP, 'user.is_superuser', false); // 当前用户是否是超级管理员
  const username = get(APP, 'user.username', null);
  const isAdmin = useMemo(() => usernames.includes(username) || isSuperuser, [isSuperuser, username, usernames]);
  return isAdmin;
};
