import React from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { PaginationProps, Tag, Space, PrimaryTableCol, TableRowData } from 'tdesign-react';

import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import OrgInfo from '@plat/modules/components/org-info';
import { getUserName } from '@src/utils';
import { getProjectTeamRouter } from '@plat/util';
import s from '@src/modules/style.scss';

// 模块内
import { TEAM_STATE_CHOICES, TeamStateEnum } from './constants';

interface TeamTableProps {
  dataSource: Array<any>;
  pagination: PaginationProps;
  loading: boolean;
  onDelete: (team: any) => void;
  onRecover: (team: any) => void;
}

const TeamTable = ({ dataSource, pagination, loading, onDelete, onRecover }: TeamTableProps) => {
  const columns: PrimaryTableCol<TableRowData>[] = [
    {
      colKey: 'display_name',
      title: t('项目名称'),
      width: 120,
      cell: ({ row }: any) => (
        <>
          {row?.status === TeamStateEnum.ACTIVE
            ? <a
              className='link-name text-weight-bold'
              href={getProjectTeamRouter(row?.organization?.org_sid, row?.name)}
              target='_blank'
              rel="noopener noreferrer"
            >
              <EllipsisTemplate>{row?.display_name}</EllipsisTemplate>
            </a>
            : <EllipsisTemplate className='text-grey-6'>{row?.display_name}</EllipsisTemplate>
          }
          <div className="text-grey-6 fs-12 mt-xs">
            {row?.name}
          </div>
        </>
      ),
    },
    {
      colKey: 'organization',
      title: t('所属团队'),
      width: 120,
      cell: ({ row }: any) => <OrgInfo org={get(row, 'organization')} />,
    },
    {
      colKey: 'admins',
      title: t('管理员'),
      width: 80,
      cell: ({ row }: any) => get(row, 'admins', [])
        .map((user: any) => getUserName(user))
        .join('; '),
    },
    {
      colKey: 'created_time',
      title: t('创建时间'),
      width: 120,
      cell: ({ row }: any) => formatDateTime(get(row, 'created_time')),
    },
    {
      colKey: 'status',
      title: t('状态'),
      width: 80,
      cell: ({ row }: any) => (
        row?.status === TeamStateEnum.ACTIVE
          ? <Tag theme='success' variant='light'>{TEAM_STATE_CHOICES[TeamStateEnum.ACTIVE]}</Tag>
          : <Tag theme='danger' variant='light'>{TEAM_STATE_CHOICES[TeamStateEnum.INACTIVE]}</Tag>
      ),
    },
    {
      colKey: 'op',
      title: t('操作'),
      width: 120,
      fixed: 'right',
      cell: ({ row }: any) => (
        <Space size='small' breakLine>
          {row?.status === TeamStateEnum.ACTIVE
            && <a onClick={() => onDelete(row)} className={s.deleteOp}>
              {t('禁用项目')}
            </a>}
          {row?.status === TeamStateEnum.INACTIVE
            && <a onClick={() => onRecover(row)}>
              {t('恢复项目')}
            </a>}
        </Space>
      ),
    },
  ];

  return (
    <Table
      rowKey='id'
      loading={loading}
      data={dataSource}
      columns={columns}
      pagination={pagination}
    />
  );
};

export default TeamTable;
