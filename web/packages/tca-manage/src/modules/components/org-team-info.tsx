import React from 'react';

// 项目内
import EllipsisTemplate from '@src/components/ellipsis';
import OrgInfo from '@src/modules/components/org-info';

interface IProps {
  org: any;
  team: any;
  maxWidth?: number;
}
const OrgAndTeamInfo = ({ org, team, maxWidth }: IProps) => {
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
