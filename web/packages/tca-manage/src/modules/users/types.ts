/** 用户详情信息结构 TableRowData */
export interface UserData {
  /** 用户username，唯一标识 */
  username: string;
  /** 昵称 */
  nickname: string;
  /** 是否超级管理员 */
  is_superuser: boolean;
  /** 用户等级 */
  level: number;
  /** 用户最近登录时间 */
  latest_login_time?: string;
  /** 用户状态 */
  status: number;
}
