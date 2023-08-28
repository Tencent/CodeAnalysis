/**
 * 获取团队路由前缀
 * @param orgSid 团队名称
 */
export const getOrgRouter = (orgSid: string) => `/t/${orgSid}`;

export const getProjectTeamRouter = (orgSid: string, teamName: string) => `/t/${orgSid}/p/${teamName}/repos`;

export const getRepoRouter = (repoInfo: any) => {
  const orgSid = repoInfo?.project_team?.org_sid;
  const teamName = repoInfo.project_team?.name;
  const repoId = repoInfo?.id;
  return `/t/${orgSid}/p/${teamName}/repos/${repoId}/member`;
};

/** 获取job详情路由地址 */
export const getJobRouter = (jobInfo: any, archived = false) => {
  const orgSid = jobInfo?.project?.organization?.org_sid;
  const teamName = jobInfo?.project?.project_team?.name;
  const repoId = jobInfo?.project?.repo_id;
  const projectId = jobInfo?.project?.id;
  const jobId = jobInfo?.id;
  return `/t/${orgSid}/p/${teamName}/code-analysis/repos/${repoId}/projects/${projectId}/scan-history/${jobId}/detail${archived ? '?jobArchived=true' : ''}`;
};

/** 获取工具详情路由地址 */
export const getToolRouter = (toolInfo: any) => `/t/${toolInfo?.org_detail?.org_sid}/tools/${toolInfo?.id}/rules`;

export const getScanConfRouter = (tab: string) => `/manage/scanconf/${tab}`;
