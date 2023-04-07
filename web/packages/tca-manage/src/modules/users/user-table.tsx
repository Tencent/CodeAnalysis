import React from 'react';
import { t } from '@src/utils/i18n';
import cn from 'classnames';
import { Tag, PaginationProps, PrimaryTableCol } from 'tdesign-react';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

// 模块内
import { LEVEL_CHOICES, LevelEnum, StatusEnum } from './constants';
import { UserData } from './types';
import s from '../style.scss';

interface UserTableProps {
  dataSource: UserData[];
  pagination: PaginationProps;
  onEdit: (user: UserData) => void;
}

const UserTable = ({ dataSource, pagination, onEdit }: UserTableProps) => (
    <Table
      rowKey='username'
      data={dataSource}
      columns={[
        {
          colKey: 'username',
          title: t('账户'),
          width: 120,
        },
        {
          colKey: 'nickname',
          title: t('昵称'),
          width: 120,
        },
        {
          colKey: 'is_superuser',
          title: t('超级管理员'),
          width: 80,
          cell: ({ row }) => (row.is_superuser
            ? <Tag theme="success" variant='light'>是{ }</Tag>
            : <Tag>否</Tag>),
        },
        {
          colKey: 'level',
          title: t('级别'),
          width: 100,
          cell: ({ row }) => <Tag className={cn(s.userTag, s[`level-${row.level}`])}>
            {LEVEL_CHOICES[row.level as LevelEnum]}
          </Tag>,
        },
        {
          colKey: 'status',
          title: t('状态'),
          width: 80,
          cell: ({ row }) => (row.status > StatusEnum.ACTIVE ? (
            <Tag>待激活</Tag>
          ) : (
            <Tag theme="success" variant='light'>已激活</Tag>
          )),
        },
        {
          colKey: 'latest_login_time',
          title: t('最近访问时间'),
          width: 150,
          cell: ({ row }) => formatDateTime(row.latest_login_time),
        },
        {
          colKey: 'op',
          title: t('操作'),
          width: 80,
          fixed: 'right',
          cell: ({ row }) => (
            <a onClick={() => onEdit(row)}>{t('编辑')}</a>
          ),
        },
      ] as PrimaryTableCol<UserData>[]}
      pagination={pagination}
    />
);


export default UserTable;
