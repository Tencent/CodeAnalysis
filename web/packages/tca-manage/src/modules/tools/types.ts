/** 工具详情数据结构 */
export interface ToolData {
  /** ID */
  id: number;
  /** 工具虚拟名称 */
  virtual_name: string;
  /** 工具展示名称 */
  display_name: string;
  /** 是否使用 display_name */
  show_display_name: boolean;
  /** 工具名称 */
  name: string;
  /** 描述 */
  description: string;
  /** 团队信息 */
  org_detail?: {
    /** 团队名称 */
    name: string;
    /** 团队唯一标识 */
    org_sid: string;
  };
  /** 所有人可协同 */
  open_maintain: boolean;
  /** 所有人可使用 */
  open_user: boolean;
  /** 运营状态 */
  status: number;
  /** 是否需要编译 */
  build_flag: boolean;
  /** 创建人 */
  creator: string
  /** 创建时间 */
  created_time: string;
  /** 修改时间 */
  modified_time: string;
  // "languages": [
  //   "python"
  // ],
  // "scan_app": "codelint",
  // "license": "自研",
  // "scm_url": "",
  // "run_cmd": "",
  // "envs": null,
  // "scm_type": "git",
  // "tool_key": "default",
  // "scm_auth": null,
  // "task_processes": [
  //   1,
  //   2,
  //   3
  // ]
}
