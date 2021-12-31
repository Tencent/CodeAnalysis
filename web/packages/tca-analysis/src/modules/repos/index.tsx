import React, { useEffect } from 'react';
import { useParams, useHistory, useRouteMatch } from 'react-router-dom';
import { get } from 'lodash';

// 项目内
import { useStateStore } from '@src/context/store';
import { getReposRouter } from '@src/utils/getRoutePath';

// 模块内
import ReposList from './repo-list';
import { getRepoRouter } from './routes';

const Repos = () => {
  const history = useHistory();
  const { org_sid: orgSid, team_name: teamName }: any = useParams();
  const { url } = useRouteMatch();
  const { curRepo, repos } = useStateStore();

  /**
     * 重定向到对应代码库。如果store中存在代码库且在代码库列表中，则跳转到对应代码库，否则选取第一个代码库跳转
     * @param repoList 代码库列表
     */
  // const replaceToRepo = () => {
  //     if (reposLoading) {
  //     if (repos.length > 0) {
  //         // 存在登记的代码库，且repoId不存在或不在repos内则重定向到第一项
  //         if (!repoId || !repos.some((item: any) => item.id === repoId)) {
  //             if (!repos.some((item: any) => item.id === curRepo.id)) {
  //                 history.replace(getRepoRouter(org_sid, team_name, repos[0].id));
  //             } else {
  //                 history.replace(getRepoRouter(org_sid, team_name, curRepo.id));
  //             }
  //         } else {
  //             // 存在repoId则直接采用该路由
  //         }
  //     } else {
  //         // 待移除
  //         // 未登记代码库，则重定向到欢迎页
  //         history.replace(`${getReposRouter(org_sid, team_name)}/welcome`);
  //     }
  //     }
  // };

  // useEffect(() => {
  //     // 当处于xxx/repos路由时，进行重定向到对应代码库
  //     if (!reposLoading && url === getReposRouter(org_sid, team_name)) {
  //         replaceToRepo();
  //     }
  // });

  useEffect(() => {
    // 当处于xxx/repos路由时，且当前repo存在repos中，且当前路由的项目标识与当前代码库项目标识相同，则进行重定向到对应代码库
    if (
      url === getReposRouter(orgSid, teamName)
            && repos.some((item: any) => item.id === curRepo.id)
            && get(curRepo, 'project_team.name') === teamName
    ) {
      history.replace(`${getRepoRouter(orgSid, teamName, curRepo.id)}`);
    }
  });

  return <ReposList repos={repos} />;
};
export default Repos;
