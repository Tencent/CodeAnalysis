import { useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { uniqBy } from 'lodash';
import { useStateStore } from '@src/context/store';


/**
 * 获取当前页面查询参数 hooks
 */
export const useQuery = () => new URLSearchParams(useLocation().search);


/**
 * 获取项目成员
 */
export const useProjectMembers = () => {
  const { projectMembers } = useStateStore();
  return useMemo(() => {
    const { admins, users } = projectMembers;
    return uniqBy([...admins, ...users], 'username');
  }, [projectMembers]);
};
