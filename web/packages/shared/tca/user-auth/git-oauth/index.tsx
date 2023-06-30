import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { t } from 'i18next';
import { Result } from 'coding-oa-uikit';
import s from './style.scss';
import Loading from 'coding-oa-uikit/lib/icon/Loading';

// 项目内
import { getURLSearch } from '../../../util/route';
import { FetchAPIManager } from '../../../util/fetch';
import { PostMessageType, PostMessageCode, postMessageToTarget } from '../../../util/window';

enum OauthStateEnum {
  LOADING,
  SUCCESS,
  FAIL,
}

interface GitOAuthCallbackProps {
  /** auth 接口模块 */
  oauthCallback: FetchAPIManager
}

const GitOAuthCallback = ({ oauthCallback }: GitOAuthCallbackProps) => {
  const query = getURLSearch();
  const { scmPlatformName }: any = useParams();
  const [oauthState, setOauthState] = useState<OauthStateEnum>(OauthStateEnum.LOADING);
  const [errorInfo, setErrorInfo] = useState<string>('');

  useEffect(() => {
    const { opener } = window;
    oauthCallback.getDetail(scmPlatformName, query).then(() => {
      setOauthState(OauthStateEnum.SUCCESS);
      setTimeout(() => window.close(), 1000);
      postMessageToTarget(opener, { code: PostMessageCode.SUCCESS, type: PostMessageType.GIT_OAUTH });
    }, (e: any) => {
      setErrorInfo(e?.detail);
      setOauthState(OauthStateEnum.FAIL);
      postMessageToTarget(opener, { code: PostMessageCode.FAIL, type: PostMessageType.GIT_OAUTH });
    });
  }, []);

  if (oauthState === OauthStateEnum.LOADING) {
    return (
      <div className={s.oauthNote}>
        <Result
          title={t('OAuth授权中')}
          icon={<Loading />}
        />
      </div>
    );
  }

  return (
    <div className={s.oauthNote}>
      {oauthState === OauthStateEnum.SUCCESS ? <Result
        title={t('OAuth授权成功')}
        subTitle="窗口将在 1 秒后关闭。"
        status="success"
      /> : <Result
        status="error"
        title={t('OAuth授权失败')}
        subTitle={errorInfo}
      />}
    </div>
  );
};

export default GitOAuthCallback;
