import React from 'react';

// 项目内
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';
import OrgInfo from '@plat/modules/components/org-info';

interface OrgAndTeamInfoProps {
  org: any;
  team: any;
  project: any;
  maxWidth?: number;
}
const OrgAndTeamInfo = ({ org, team, project, maxWidth }: OrgAndTeamInfoProps) => (
  <>
    <OrgInfo org={org} />
    <EllipsisTemplate className=" text-grey-6 fs-12" maxWidth={maxWidth || 400}>
      {team.display_name} / {project.name}
    </EllipsisTemplate>
  </>
);

export default OrgAndTeamInfo;
