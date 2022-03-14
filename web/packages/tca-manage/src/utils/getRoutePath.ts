/**
 * 获取团队路由前缀
 * @param orgSid 团队名称
 */
export const getOrgRouter = (orgSid: string) => `/t/${orgSid}`;

export const getProjectTeamRouter = (orgSid: string, teamName: string) => `/t/${orgSid}/p/${teamName}/repos`;

export const getRepoRouter = (orgSid: string, teamName: string, repoId: number | string) => `/t/${orgSid}/p/${teamName}/repos/${repoId}/member`;

export const getJobRouter = (
  orgSid: string,
  teamName: string,
  repoId: number,
  projectId: number,
  jobId: number,
) => `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects/${projectId}/scan-history/${jobId}`;

export const getProjectRouter = (orgSid: string, teamName: string, projectId: number) => `/o/${orgSid}/t/${teamName}/pkg-analysis/${projectId}`;

export const getToolRouter = (orgSid: string, toolId: number) => `/t/${orgSid}/tools/${toolId}/rules`;
