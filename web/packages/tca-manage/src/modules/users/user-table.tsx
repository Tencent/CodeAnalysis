import React from 'react';
import { Table, Tag, Button } from 'coding-oa-uikit';
import Success from 'coding-oa-uikit/lib/icon/Success';
import Unstable from 'coding-oa-uikit/lib/icon/Unstable';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import { LEVEL_CHOICES, LEVEL_TAG_CHOICES, STATUS_ENUM } from './constants';

const { Column } = Table;

interface IProps {
  dataSource: Array<any>;
  pagination: any;
  onEdit: (user: any) => void;
}

const UserTable = ({ dataSource, pagination, onEdit }: IProps) => (
  <>
    <Table
      pagination={pagination}
      rowKey={(item: any) => item.username}
      dataSource={dataSource}
    >
      <Column title={t('账户')} dataIndex="username" />
      <Column title={t('昵称')} dataIndex="nickname" />
      <Column
        title={t('超级管理员')}
        dataIndex="is_superuser"
        render={(is_supeuser: boolean) => (is_supeuser ? <Success /> : <Unstable />)}
      />
      <Column
        title={t('级别')}
        dataIndex="level"
        render={(level: number) => (
          <Tag color={LEVEL_TAG_CHOICES[level]}>{LEVEL_CHOICES[level]}</Tag>
        )}
      />
      <Column
        title={t('状态')}
        dataIndex="status"
        render={(status: number) => (status > STATUS_ENUM.ACTIVE ? (
          <Tag>待激活</Tag>
        ) : (
          <Tag color="success">已激活</Tag>
        ))
        }
      />
      <Column
        title={t('操作')}
        dataIndex="op"
        render={(_: any, user: any) => (
          <>
            <Button onClick={() => onEdit(user)}>{t('编辑')}</Button>
          </>
        )}
      />
    </Table>
  </>
);

export default UserTable;
