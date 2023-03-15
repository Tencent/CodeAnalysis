import React from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { PaginationProps, Tag, Space, PrimaryTableCol, TableRowData, Divider } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { getOrgRouter } from '@plat/util';
import s from '@src/modules/style.scss';

// 模块内
import {
  OrgStatusEnum,
  ORG_STATUS_CHOICES,
} from './constants';

interface OrgTableProps {
  dataSource: Array<any>;
  pagination: PaginationProps;
  loading: boolean;
  onDelete: (org: any) => void;
  onRecover: (org: any) => void;
}

const OrgTable = ({ dataSource, pagination, loading, onDelete, onRecover }: OrgTableProps) => {
  const history = useHistory();

  const columns: PrimaryTableCol<TableRowData>[] = [
    {
      colKey: 'name',
      title: t('团队名称'),
      width: 160,
      cell: ({ row }: any) => (
        <>
          {row?.status === OrgStatusEnum.ACTIVE
            ? <a
              className='link-name text-weight-bold'
              href={`${getOrgRouter(row?.org_sid)}/${row?.repo_count !== 0 ? 'workspace' : 'projects'}`}
              target='_blank'
              rel="noopener noreferrer"
            >
              <EllipsisTemplate>{row?.name}</EllipsisTemplate>
            </a>
            : <EllipsisTemplate className='text-grey-6'>{row?.name}</EllipsisTemplate>
          }
          <div className="text-grey-6 fs-12 mt-xs">
            {row?.owner} / {row?.tel_number} / {formatDateTime(row?.created_time)}
          </div>
        </>
      ),
    },
    {
      colKey: 'overview',
      title: t('团队概览'),
      width: 120,
      cell: ({ row }: any) => (
        <Space className='text-grey-7 text-center' align="center" separator={<Divider layout="vertical" />}>
          <div>
            {row.user_count}
            <p className='fs-12'>{t('成员数')} </p>
          </div>
          <div>
            {row.team_count}
            <p className='fs-12'>{t('项目数')}</p>
          </div>
          <div>
            {row.repo_count}
            <p className='fs-12'>{t('代码库')} </p>
          </div>
        </Space>
      ),
    },
    {
      colKey: 'status',
      title: t('状态'),
      width: 80,
      cell: ({ row }: any) => (
        row?.status === OrgStatusEnum.FORBIDEN
          ? <Tag theme='danger' variant='light'>{ORG_STATUS_CHOICES[OrgStatusEnum.FORBIDEN]}</Tag>
          : <Tag theme='success' variant='light'>{ORG_STATUS_CHOICES[OrgStatusEnum.ACTIVE]}</Tag>
      ),
    },
    {
      colKey: 'op',
      title: t('操作'),
      width: 60,
      fixed: 'right',
      cell: ({ row }: any) => (
        <>
          <Space size='small' breakLine>
            <a
              onClick={() => {
                history.push(`/manage/teams?organization=${row?.id}`);
              }}
            >
              {t('查看项目')}
            </a>
            {row?.status === OrgStatusEnum.FORBIDEN
              ? <a onClick={() => onRecover(row)}>
                {t('恢复团队')}
              </a> : <a onClick={() => onDelete(row)} className={s.deleteOp}>
                {t('禁用团队')}
              </a>}
          </Space>
        </>
      ),
    },
  ];

  return (
    <Table
      loading={loading}
      data={dataSource}
      columns={columns}
      pagination={pagination}
    />
  );
};

export default OrgTable;
