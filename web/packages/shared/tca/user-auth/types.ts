import { FetchAPIManager } from '../../util/fetch';

/** OAuth 凭证相关返回结果数据结构 */
export type OAuthResult = {
  [key: string]: string
};

/** user auth api 数据结构  */
export type UserAuthAPI = {
  /** 个人凭证列表 */
  getAuths: () => Promise<any[]>,
  /** 个人凭证信息列表 */
  getAuthInfos: () => Promise<{
    oauthList: any[],
    sshList: any[],
    accountList: any[]
  }>,
  /** ssh 凭证接口 */
  ssh: FetchAPIManager,
  /** account 凭证接口 */
  account: FetchAPIManager,
  /** oauth 凭证接口 */
  oauth: FetchAPIManager,
  /** oauth 凭证后台配置项接口 */
  oauthSetting: FetchAPIManager,
  /** oauth 凭证个人认证项接口 */
  oauthStatus: FetchAPIManager,
  /** oauth 授权回调接口 */
  oauthCallback: FetchAPIManager
};
