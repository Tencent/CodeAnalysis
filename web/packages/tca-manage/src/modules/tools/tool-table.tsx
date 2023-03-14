import React from 'react';
import { t } from '@src/utils/i18n';
import cn from 'classnames';
import { PaginationProps, Tag, Space, PrimaryTableCol } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

// 项目内
import { getToolRouter, toolUtil } from '@plat/util';

// 模块内
import { STATUS_CHOICES, StatusEnum } from './constants';
import { ToolData } from './types';
import s from '../style.scss';


interface ToolTableProps {
  dataSource: ToolData[];
  pagination: PaginationProps;
  loading: boolean;
  onEdit: (tool: ToolData) => void;
}

const ToolTable = ({ dataSource, pagination, loading, onEdit }: ToolTableProps) => {
  const columns: PrimaryTableCol<ToolData>[] = [
    {
      colKey: 'display_name',
      title: t('工具名称&简介'),
      width: 200,
      fixed: 'left',
      cell: ({ row }) => (
        <>
          <a
            className="link-name text-weight-bold"
            href={getToolRouter(row)}
            target='_blank'
            rel="noopener noreferrer"
          >
            {toolUtil.getName(row)}
          </a>
          <div className="mt-xs fs-12 text-grey-6">
            <EllipsisTemplate>{row.description}</EllipsisTemplate>
          </div>
        </>
      ),
    },
    {
      colKey: 'org_detail',
      title: t('提供方'),
      width: 120,
      cell: ({ row }) => row.org_detail?.name,
    },
    {
      colKey: 'created_time',
      title: t('创建时间'),
      width: 100,
      cell: ({ row }) => formatDateTime(row.created_time),
    },
    {
      colKey: 'modified_time',
      title: t('最近修改时间'),
      width: 100,
      cell: ({ row }) => formatDateTime(row.modified_time),
    },
    {
      colKey: 'status',
      title: t('状态'),
      width: 120,
      cell: ({ row }) => (
        <Tag className={cn(s.toolTag, s[`status-${row.status}`])}>
          {STATUS_CHOICES[row.status as StatusEnum]}
        </Tag>
      ),
    },
    {
      colKey: 'other',
      title: t('权限状态'),
      width: 120,
      cell: ({ row }) => {
        if (row.open_maintain) {
          return (
            <Space size='small' breakLine>
              <Tag className={cn(s.toolTag, s.maintain)}>支持自定义规则</Tag>
              <Tag className={cn(s.toolTag, s.default)}>全平台可用</Tag>
            </Space>
          );
        }
        if (row.open_user) {
          return (
            <>
              <Tag className={cn(s.toolTag, s.default)}>全平台可用</Tag>
            </>
          );
        }
        return (
          <>
            <Tag className={cn(s.toolTag, s.custom)}>团队内可用</Tag>
          </>
        );
      },
    },
    {
      colKey: 'op',
      title: t('操作'),
      width: 100,
      fixed: 'right',
      cell: ({ row }) => <a onClick={() => onEdit(row)}>{t('权限调整')}</a>,
    },
  ];

  return (
    <Table
      data={dataSource}
      loading={loading}
      columns={columns}
      pagination={pagination}
    />
  );
};

export default ToolTable;
