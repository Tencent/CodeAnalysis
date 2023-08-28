
import { useSelector } from 'react-redux';

import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';

import { NAMESPACE, UserState } from '@src/store/user';

/** 获取用户团队权限 */
export const useOrgAdminPerm = () => {
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const isAdmin: boolean = useSelector((state: any) => state.APP)?.isOrgAdminUser ?? false;
  const isSuperuser: boolean = userinfo?.is_superuser;
  return [isSuperuser || isAdmin, isAdmin, isSuperuser];
};
