import React, { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import Loading from '@tencent/micro-frontend-shared/component/loading';
import { getURLSearch } from '@tencent/micro-frontend-shared/util/route';
import { PostMessageType, PostMessageCode, postMessageToTarget } from '@tencent/micro-frontend-shared/util/window';

import { message } from 'coding-oa-uikit';

import Container from '@src/component/container';
import { UserAPI } from '@plat/api';

const GitOAuth = () => {
  const query = getURLSearch();
  const { scmPlatformName }: any = useParams();
  const { t } = useTranslation();

  useEffect(() => {
    const { opener } = window;
    UserAPI.getOAuthCallback(scmPlatformName, query).then(() => {
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
    <Container>
      <Loading msg={t('OAuth授权中')} />
    </Container>
  );
};

export default GitOAuth;
