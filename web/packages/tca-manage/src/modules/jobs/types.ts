/** 团队数据结构 */
interface OrgData {
  /** 团队唯一标识 */
  org_sid: string;
  /** 团队名称 */
  name: string;
  /** 团队级别 */
  level: number;
  /** 团队使用状态 */
  status: number
}

/** 项目组数据结构 */
interface TeamData {
  /** 项目组名称，唯一标识 */
  name: string;
  /** 项目组展示名称 */
  display_name: string;
  /** 团队唯一标识 */
  org_sid: string;
  /** 项目组状态 */
  status: number
}

/** 分析项目数据结构 */
interface ProjectData {
  /** 分析项目ID */
  id: number;
  /** 分支名称 */
  branch: string;
  /** 代码库ID */
  repo_id: number;
  /** 代码库地址 */
  repo_scm_url: string;
  /** 分析方案ID */
  scan_scheme: number;
  /** 团队 */
  organization?: OrgData;
  /** 项目组 */
  project_team?: TeamData
}

/** Job 任务数据结构 */
export interface JobData {
  /** ID */
  id: number;
  /** 分析项目 */
  project: ProjectData;
  /** 子任务数量 */
  task_num?: number;
  /** 子任务执行完毕数量 */
  task_done: number;
  /** 任务执行状态 */
  state: number;
  /** 执行结果 code */
  result_code?: number;
  /** 执行结果 code 对应信息 */
  result_code_msg: string;
  /** 执行结果描述信息 */
  result_msg: string;
  /** 等待耗时 */
  waiting_time: string;
  /** 执行耗时 */
  execute_time: string;
  /** 数据入库耗时 */
  save_time: string;
  /** 创建时间 */
  create_time: string;
  /** 创建渠道 */
  created_from: string;
  /** 创建人 */
  creator: string;
  /** 启动时间 */
  start_time: string;
  /** 执行结束数据 */
  end_time: string;
  /** 扫描任务ID */
  scan_id: number;
  // blank_line_num: 5529
  // code_line_num: 337313
  // comment_line_num: 15447
  // context_path: "http://127.0.0.1:8000/files/public_server_temp/jobdata/projects/137/job965/e6443586132611edb06a525400f4bf4b/job_context.json"
  // efficient_comment_line_num: null
  // end_time: "2022-08-03T20:33:31.954917+08:00"
  // expire_time: null
  // filtered_efficient_comment_line_num: null
  // remarked_by: null
  // remarks: null
  // result_path: null
  // tasks: [,…]
  // total_line_num: 358289
}

export interface TaskData {
  /** ID */
  id: number;
  /** 模块 */
  module: string;
  /** 任务名称 */
  task_name: string;
  /** 运行标签 */
  tag: string;
  /** 任务执行状态 */
  state: number;
  /** 执行结果 code */
  result_code?: number;
  /** 执行结果 code 对应信息 */
  result_code_msg: string;
  /** 执行结果描述信息 */
  result_msg: string;
  /** 执行耗时 */
  execute_time: string;
  /** 整体耗时 */
  total_time: string;
  /** 创建时间 */
  create_time: string;
  /** 启动时间 */
  start_time: string;
  /** 执行结束数据 */
  end_time: string;
  /** Job */
  job: {
    id: number;
    project?: ProjectData;
    blank_line_num: number;
    code_line_num: number;
    comment_line_num: number;
    state: number;
    total_line_num: number;
  };
}
