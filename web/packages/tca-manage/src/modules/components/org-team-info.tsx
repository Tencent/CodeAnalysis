import React from 'react';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';

// 项目内
import OrgInfo from '@plat/modules/components/org-info';

interface OrgAndTeamInfoProps {
  org: any;
  team: any;
  maxWidth?: number;
}
const OrgAndTeamInfo = ({ org, team, maxWidth }: OrgAndTeamInfoProps) => {
  if (!org || !team) {
    return <>- -</>;
  }
  return (
    <>
      <OrgInfo org={org} />
      <EllipsisTemplate className=" text-grey-6 fs-12" maxWidth={maxWidth}>
        {team.display_name}
      </EllipsisTemplate>
    </>
  );
};

export default OrgAndTeamInfo;
