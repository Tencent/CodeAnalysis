import { useParams as useDefaultParams } from 'react-router-dom';

/** 路由参数 */
export interface RouteParams {
  /** 团队唯一标识 */
  orgSid?: string;
  /** 团队名称 */
  teamName?: string;
  /** 代码库ID */
  repoId?: string;
  /** 分析项目ID */
  projectId?: string;
  /** 分析方案ID */
  schemeId?: string;
  /** 文件ID */
  fileId?: string;
  /** Job ID */
  jobId?: string;
  /** 规则包 ID */
  pkgId?: string;
  /** 工具名称 */
  toolName?: string;
  /** 其他参数 */
  [key: string]: string;
}

/** useParams */
const useParams = useDefaultParams<RouteParams>;

export default useParams;
