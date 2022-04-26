// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

export const getHomeRouter = () => '/';

export const getTeamsRouter = () => '/teams';

export const getManageRouter = () => '/manage';

export const getTeamRouter = (orgSid: string) => `/t/${orgSid}`;

export const getToolsRouter = (orgSid: string) => `/t/${orgSid}/tools`;

export const getProjectRouter = (orgSid: string, name: string) => `/t/${orgSid}/p/${name}`;

export const getRepoRouter = (orgSid: string, teamName: string, repoId: number | string) => `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects`;

export const getRepoProjectRouter = (orgSid: string, teamName: string, repoId: number | string, projectId: number | string) => `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects/${projectId}/overview`;

export const DOC_PATH = '/document/';
export const API_DOC_PATH = '/document/zh/api/';
