import React from 'react';
import { Tooltip, Row, Col } from 'coding-oa-uikit';
import InfoCircle from 'coding-oa-uikit/lib/icon/InfoCircle';

// 项目内
import EllipsisTemplate from '@src/components/ellipsis';
import { formatDateTime } from '@src/utils';

const LEVEL_ENUM = {
  NORMAL: 1,
  VIP: 2,
  SUPER_VIP: 3,
};

const LEVEL_CHOICES = {
  [LEVEL_ENUM.NORMAL]: '普通团队',
  [LEVEL_ENUM.VIP]: 'VIP 团队',
  [LEVEL_ENUM.SUPER_VIP]: '超级 VIP 团队',
};

interface IProps {
  org: any;
  maxWidth?: number;
}
const OrgInfo = ({ org, maxWidth }: IProps) => (
  <Row style={{ minWidth: '100px' }} gutter={8}>
    <Col>
      <EllipsisTemplate maxWidth={maxWidth}>{org.name}</EllipsisTemplate>
    </Col>
    <Col flex="auto">
      <Tooltip
        title={
          <div style={{ width: '250px' }}>
            <div>团队名称：{org.name}</div>
            <div>负责人：{org.owner}</div>
            <div>联系方式：{org.tel_number}</div>
            <div>团队级别：{LEVEL_CHOICES[org.level]}</div>
            <div>创建时间：{formatDateTime(org.created_time)}</div>
          </div>
        }
      >
        <InfoCircle className="cursor-pointer" />
      </Tooltip>
    </Col>
  </Row>
);

export default OrgInfo;
