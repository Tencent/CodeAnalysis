/** OAuth配置数据结构 */
export interface OAuthSettingData {
  /** ID */
  id?: number;
  /** OAuth平台ID */
  client_id?: string;
  /** OAuth平台密钥 */
  client_secret?: string;
  /** 重定向地址 */
  redirect_uri?: string
  /** 凭证平台类型 */
  scm_platform: number;
  /** 平台描述 */
  scm_platform_desc: string
  /** 平台名称 */
  scm_platform_name: string
}
