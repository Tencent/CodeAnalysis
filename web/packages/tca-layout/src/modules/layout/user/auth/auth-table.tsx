// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import { Table, Button } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { AUTH_TYPE_CHOICES, AUTH_TYPE, SCM_PLATFORM } from '@src/utils/constant';

interface IProps {
  dataSource: Array<any>;
  onEdit?: (authinfo: any) => void;
  onDel?: (authinfo: any) => void;
}
const AuthTable = (props: IProps) => {
  const { dataSource, onEdit, onDel } = props;

  const columns = [
    {
      title: t('平台'),
      dataIndex: 'scm_platform',
      key: 'scm_platform',
      width: 200,
      render: (scm_platform: string, recode: any) => (
        <>
          <span>{get(SCM_PLATFORM, scm_platform) || scm_platform}</span>
          <p className="text-grey-7 fs-12">{recode.scm_platform_desc}</p>
        </>
      ),
    },
    {
      title: t('凭证'),
      dataIndex: 'scm_username',
      key: 'scm_username',
      width: 200,
      render: (scm_username: string, authinfo: any) => (
        <div className=" text-weight-medium">
          {AUTH_TYPE_CHOICES[authinfo.auth_type]} {t('：')}
          {authinfo.auth_type === AUTH_TYPE.HTTP ? scm_username : authinfo.name}
        </div>
      ),
    },
    {
      title: t('操作'),
      dataIndex: 'op',
      key: 'op',
      width: 200,
      render: (_: string, authinfo: any) => (
        <>
          <Button
            type="text"
            icon={<Edit />}
            onClick={() => onEdit?.(authinfo)}
          />
          <Button type="text" icon={<Trash />} onClick={() => onDel?.(authinfo)} />
        </>
      ),
    },
  ];
  return (
    <Table
      pagination={{
        showTotal: (total: number, range: [number, number]) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
      }}
      rowKey={(item: any) => `${item.auth_type}#${item.id}`}
      dataSource={dataSource}
      columns={columns}
    />
  );
};

export default AuthTable;
