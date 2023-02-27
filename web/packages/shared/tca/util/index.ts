/**
 * 获取代码库地址 path
 * @param scmUrl scm url
 * @returns path
 */
export const getScmUrlPath = (scmUrl: string) => {
  // 处理 ssh http 格式 scm url
  const path = scmUrl.replace(/(^https?:\/\/[^/]*\/)|(^git@[^:]*:([0-9]*\/)?)/, '');
  return path;
};

interface GetRepoNameParams {
  /** 是否仅使用代码库尾部作为name，否则将代码库path作为name */
  onlyLastName: boolean
}

/**
 * 获取代码库展示名称
 * @param repoInfo 代码库信息，可传入{name, url, scmUrl, scm_url}，默认存在name直接显示，否则会格式化处理
 * @param params 参数项
 * @returns repoName
 */
export const getRepoName = (repoInfo: any, params: GetRepoNameParams = { onlyLastName: false }) => {
  const info = repoInfo || {};
  const { name, url, scmUrl } = info;
  if (name) {
    return name;
  }
  const repoUrl = url || scmUrl || info.scm_url;
  if (repoUrl) {
    if (params.onlyLastName) {
      return repoUrl.substring(repoUrl.lastIndexOf('/') + 1);
    }
    return getScmUrlPath(repoUrl);
  }
  return '';
};

