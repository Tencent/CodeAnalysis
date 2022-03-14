import React from 'react';

// 项目内
import EllipsisTemplate from '@src/components/ellipsis';
import OrgInfo from '@src/modules/components/org-info';

interface IProps {
  org: any;
  team: any;
  project: any;
  maxWidth?: number;
}
const OrgAndTeamInfo = ({ org, team, project, maxWidth }: IProps) => (
  <>
    <OrgInfo org={org} />
    <EllipsisTemplate className=" text-grey-6 fs-12" maxWidth={maxWidth || 400}>
      {team.display_name} / {project.name}
    </EllipsisTemplate>
  </>
);

export default OrgAndTeamInfo;
