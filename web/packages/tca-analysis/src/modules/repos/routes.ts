// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import { getBaseRouter } from '@src/utils/getRoutePath';
import { REPO_TAB_TYPE } from './constants';

/**
 * 获取代码库路由， 默认路由到成员页面
 * @param repoId 代码库ID
 */
export const getRepoRouter = (
  org_sid: string,
  team_name: string,
  repoId: number | string,
  tabKey: string = REPO_TAB_TYPE.MEMBER,
) => `${getBaseRouter(org_sid, team_name)}/repos/${repoId}/${tabKey}`;

export const getPCAuthRouter = () => '/user/auth';
