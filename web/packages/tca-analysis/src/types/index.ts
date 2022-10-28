export interface TemplateRouteParams {
  project: string;
  id?: string;
  tab?: string;
}

export interface ToolsRouteParams {
  project: string;
  tab?: string;
}

export interface ProjectRouteParams {
  project?: string; // coding 项目名称，仅 coding OA
  repoId: string;
  projectId?: string;
  tab?: string;
  metricTab?: string; // 度量结果tab
  jobId?: string; // 分析历史 - 分析详情ID
  scanTab?: string; // 分析历史 - 分析详情tab
  toolName?: string; // 扩展功能 - 工具名称
  authorName?: string; // 历史趋势 - 用户名称
}

export interface RestfulListAPIParams {
  results: any[];
  count: number;
  next: string;
  previous: string
}

export interface stringKey {
  [key: string]: string;
}

export interface numberKey {
  [key: number]: string;
}

export interface anyKey {
  [key: string | number]: any;
}
