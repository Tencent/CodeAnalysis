import React, { useEffect } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import Loading from '@tencent/micro-frontend-shared/component/loading';

import { addMemberByInvite } from '@src/services/team';


const OrgInvite = () => {
  const params: any = useParams();

  const history = useHistory();

  useEffect(() => {
    addMemberByInvite(decodeURIComponent(params.code))
      .then((response: any) => {
        history.replace(`/t/${response.org_sid}/profile`);
      })
      .catch(() => {
        history.replace('/');
      });
  }, []);

  return (
    <Loading />
  );
};

export default OrgInvite;
