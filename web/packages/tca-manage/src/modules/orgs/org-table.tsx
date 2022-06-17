import React from 'react';
import { Link, useHistory } from 'react-router-dom';
import { Table, Tag, Tooltip, Button, Statistic, Row, Col, Card } from 'coding-oa-uikit';
import Project from 'coding-oa-uikit/lib/icon/Project';
import Repos from 'coding-oa-uikit/lib/icon/Repos';
import Group from 'coding-oa-uikit/lib/icon/Group';
import Undo from 'coding-oa-uikit/lib/icon/Undo';
import Stop from 'coding-oa-uikit/lib/icon/Stop';

// 项目内
import { t } from '@src/i18n/i18next';
import EllipsisTemplate from '@src/components/ellipsis';
import { formatDateTime } from '@src/utils';
import { getOrgRouter } from '@src//utils/getRoutePath';

// 模块内
import {
  ORG_STATUS_ENUM,
  ORG_STATUS_CHOICES,
} from './constants';

const FormatStatus = (org: any) => {
  const status = org?.status;
  const info = status === ORG_STATUS_ENUM.ACTIVE ? {
    text: ORG_STATUS_CHOICES[ORG_STATUS_ENUM.ACTIVE],
    color: 'success',
  } : {
    text: ORG_STATUS_CHOICES[ORG_STATUS_ENUM.INACTIVE],
    color : 'red',
  };
  return (
    <Tag color={info.color}>{info.text}</Tag>
  );
};

const FormatName = (org: any) => (
  <>
    {org?.status === ORG_STATUS_ENUM.ACTIVE 
    ? <Link
      to={`${getOrgRouter(org.org_sid)}/${org.repo_count !== 0 ? 'workspace' : 'projects'}`}
    >
      <EllipsisTemplate>{org.name}</EllipsisTemplate>
    </Link>
    : <EllipsisTemplate>{org.name}</EllipsisTemplate>
    }
    <div className="text-grey-6 fs-12 mt-sm">
      {org.owner} / {org.tel_number} / {formatDateTime(org.created_time)}
    </div>
  </>
);

const FormatOverview = (org: any) => (
  <Row gutter={8}>
    <Col span="8">
      <Card size="small">
        <Statistic
          prefix={<Group className="mr-xs" color="#f0850a" />}
          title={<span className="fs-12">{t('成员数')}</span>}
          value={org.user_count}
          valueStyle={{ color: '#f0850a', fontSize: '14px' }}
        />
      </Card>
    </Col>
    <Col span="8">
      <Card size="small">
        <Statistic
          prefix={<Project className="mr-xs" color="3d98ff" />}
          title={<span className="fs-12">{t('项目数')}</span>}
          value={org.team_count}
          valueStyle={{ color: '#3d98ff', fontSize: '14px' }}
        />
      </Card>
    </Col>
    <Col span="8">
      <Card size="small">
        <Statistic
          prefix={<Repos className="mr-xs" color="3f8600" />}
          title={<span className="fs-12">{t('代码库')}</span>}
          value={org.repo_count}
          valueStyle={{ color: '#3f8600', fontSize: '14px' }}
        />
      </Card>
    </Col>
  </Row>
);

const FormatOp = (org: any, onDelete: (org: any) => void, onRecover: (org: any) => void) => {
  const history = useHistory();
  const status = org?.status;
  const orgSid = org?.org_sid;
  return (
    <>
      <Tooltip title={t('查看项目列表')}>
        <Button
          className="mr-sm"
          shape="circle"
          icon={<Project />}
          onClick={() => {
            history.push(`/manage/teams?organization_sid=${orgSid}`);
          }}
        />
      </Tooltip>
      {status === ORG_STATUS_ENUM.ACTIVE && <Tooltip title={t('禁用团队')}>
        <Button
          className="mr-sm"
          shape="circle"
          icon={<Stop />}
          danger
          onClick={() => onDelete(org)}
        />
      </Tooltip>}
      {status === ORG_STATUS_ENUM.INACTIVE && <Tooltip title={t('恢复团队')}>
        <Button
          className="mr-sm"
          shape="circle"
          icon={<Undo />}
          onClick={() => onRecover(org)}
        />
      </Tooltip>}
    </>
  );
};

interface IProps {
  dataSource: Array<any>;
  pagination: any;
  onDelete: (org: any) => void;
  onRecover: (org: any) => void;
}

const OrgTable = ({ dataSource, pagination, onDelete, onRecover }: IProps) => {
  const columns = [
    {
      title: t('团队名称'),
      dataIndex: 'name',
      render: (_: string, org: any) => FormatName(org),
    },
    {
      title: t('团队概览'),
      dataIndex: 'overview',
      render: (_: string, org: any) => FormatOverview(org),
    },
    {
      title: t('状态'),
      dataIndex: 'status',
      render: (_: number, org: any) => FormatStatus(org),
    },
    {
      title: t('操作'),
      dataIndex: 'op',
      render: (_: any, org: any) => FormatOp(org, onDelete, onRecover),
    },
  ];
  return (
    <>
      <Table
        pagination={pagination}
        rowKey={(item: any) => item.id}
        dataSource={dataSource}
        columns={columns}
      />
    </>
  );
};

export default OrgTable;
