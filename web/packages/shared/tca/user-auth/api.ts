import { FetchAPIManager } from '../../util/fetch';
import { AuthTypeEnum, SCM_PLATFORM_NAME_CHOICES } from './constant';
import { OAuthResult, UserAuthAPI } from './types';

export const formatUserAuthAPI = (
  /** ssh 凭证接口 */
  ssh: FetchAPIManager,
  /** account 凭证接口  */
  account: FetchAPIManager,
  /** oauth 凭证接口 */
  oauth: FetchAPIManager,
  /** oauth 凭证后台配置项接口 */
  oauthSetting: FetchAPIManager,
  /** oauth 凭证个人认证项接口 */
  oauthStatus: FetchAPIManager,
  /** oauth 认证回调接口 */
  oauthCallback: FetchAPIManager,
): UserAuthAPI => ({
  getAuths: () => Promise.all([
    ssh.get({ limit: 200 }),
    account.get({ limit: 200 }),
    oauthSetting.get(),
    oauthStatus.get(),
  ]).then(([sshInfo, accountInfo, oauthSettings, oauthStatus]) => {
    const sshList = (sshInfo as RestfulListAPIParams).results.map(item => ({ ...item, auth_type: AuthTypeEnum.SSH }));
    const accountList = (accountInfo as RestfulListAPIParams).results.map(item => ({
      ...item, auth_type: AuthTypeEnum.HTTP,
    }));
    const oauthList = Object.keys(SCM_PLATFORM_NAME_CHOICES).filter(scmPlatformName => (
      oauthSettings as OAuthResult
    )[scmPlatformName])
      .map(scmPlatformName => ({
        ...SCM_PLATFORM_NAME_CHOICES[scmPlatformName],
        platform_status: true,
        oauth_status: (oauthStatus as OAuthResult)[scmPlatformName] || false,
      }));
    return [...oauthList, ...sshList, ...accountList];
  }),
  getAuthInfos: () => Promise.all([
    ssh.get({ limit: 200 }),
    account.get({ limit: 200 }),
    oauth.get(),
    oauthStatus.get(),
  ]).then(([sshInfo, accountInfo, oauthInfo, oauthStatus]) => {
    const sshList = (sshInfo as RestfulListAPIParams).results;
    const accountList = (accountInfo as RestfulListAPIParams).results;
    const oauthList = (oauthInfo as RestfulListAPIParams).results.filter(item => (
      oauthStatus as OAuthResult
    )[item.scm_platform_name]);
    return { oauthList, sshList, accountList };
  }),
  ssh,
  account,
  oauth,
  oauthSetting,
  oauthStatus,
  oauthCallback,
});
