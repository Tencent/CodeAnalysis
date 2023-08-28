import React from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { useMount } from 'ahooks';
import { message } from 'tdesign-react';

import Loading from '@tencent/micro-frontend-shared/tdesign-component/loading';
import { addMemberByInvite } from '@src/services/team';

const OrgInvite = () => {
  const { code }: any = useParams();

  const history = useHistory();

  useMount(() => {
    addMemberByInvite(decodeURIComponent(code))
      .then((res: any) => {
        message.success('已加入团队');
        history.replace(`/t/${res.orgSid}/profile`);
      })
      .catch(() => {
        message.error('加入团队失败');
        history.replace('/');
      });
  });

  return (
    <Loading />
  );
};

export default OrgInvite;
