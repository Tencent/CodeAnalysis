import React from 'react';
import { Row } from 'tdesign-react';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';

interface OrgInfoProps {
  org: any;
  maxWidth?: number;
}
const OrgInfo = ({ org, maxWidth }: OrgInfoProps) => (
  <Row style={{ minWidth: '100px' }} gutter={4}>
    <EllipsisTemplate maxWidth={maxWidth}>
      <a className="text-grey-8" href={`/t/${org?.org_sid}/profile`} target='_blank' rel="noreferrer" >{org?.name || '- -'}</a>
    </EllipsisTemplate>
  </Row>
);

export default OrgInfo;
