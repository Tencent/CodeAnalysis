import { useEffect } from 'react';
// 项目内
import { getRepo } from '@src/services/repos';
import { getMembers } from '@src/services/common';
import { useStateStore, useDispatchStore } from '@src/context/store';
import { SET_CUR_REPO, SET_CUR_REPO_MEMBER } from '@src/context/constant';

/**
 * 初始化代码库相关信息，用户store设置代码库信息和成员等初始化配置
 * @param repoId 代码库ID
 */
export const useInitRepo = (orgSid: string, teamName: string, repoId: number | string) => {
  const { curRepo, curRepoMember } = useStateStore();
  const dispatch = useDispatchStore();

  useEffect(() => {
    if (repoId) {
      // 获取代码库信息
      getRepo(orgSid, teamName, repoId).then((response) => {
        dispatch({
          type: SET_CUR_REPO,
          payload: response,
        });
      });
      // 获取代码库成员
      getMembers(orgSid, teamName, repoId).then((response) => {
        const { admins = [], users = [] } = response;
        dispatch({
          type: SET_CUR_REPO_MEMBER,
          payload: {
            admins,
            users,
          },
        });
      });
    }
  }, [repoId]);

  return { curRepo, curRepoMember };
};
