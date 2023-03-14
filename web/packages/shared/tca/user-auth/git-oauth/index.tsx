import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { t } from 'i18next';
import { message } from 'coding-oa-uikit';

// 项目内
import Loading from '../../../component/loading';
import { getURLSearch } from '../../../util/route';
import { FetchAPIManager } from '../../../util/fetch';
import { PostMessageType, PostMessageCode, postMessageToTarget } from '../../../util/window';

interface GitOAuthCallbackProps {
  /** auth 接口模块 */
  oauthCallback: FetchAPIManager
}

const GitOAuthCallback = ({ oauthCallback }: GitOAuthCallbackProps) => {
  const query = getURLSearch();
  const { scmPlatformName }: any = useParams();

  useEffect(() => {
    const { opener } = window;
    oauthCallback.getDetail(scmPlatformName, query).then(() => {
      message.success(t('OAuth授权成功'));
      postMessageToTarget(opener, { code: PostMessageCode.SUCCESS, type: PostMessageType.GIT_OAUTH });
    })
      .catch(() => {
        message.error(t('OAuth授权失败'));
        postMessageToTarget(opener, { code: PostMessageCode.FAIL, type: PostMessageType.GIT_OAUTH });
      })
      .finally(() => {
        window.close();
      });
  }, []);

  return (
    <Loading msg={t('OAuth授权中')} />
  );
};

export default GitOAuthCallback;
