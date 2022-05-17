import React from 'react';
import { Table, Button } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import { SCM_PLATFORM } from './constants';

interface IProps {
  dataSource: Array<any>;
  onEdit: (platform_info: any) => void;
  onDelete: (platform_info: any) => void;
}

const OAuthTable = ({ dataSource, onEdit, onDelete }: IProps) => {

  const columns = [
    {
      title: t('平台'),
      dataIndex: 'scm_platform',
      key: 'scm_platform',
      render: (scm_platform: number) => (
        <span>{get(SCM_PLATFORM, scm_platform) || scm_platform}</span>
      ),
    },
    {
      title: t('平台描述'),
      dataIndex: 'scm_platform_desc',
      key: 'scm_platform_desc',
      render: (scm_platform_desc: number) => (
        <span>{scm_platform_desc}</span>
      ),
    },
    {
      title: t('Client ID'),
      dataIndex: 'client_id',
      key: 'client_id',
      render: (client_id: string) => (
        <span>{client_id}</span>
      ),
    },
    {
      title: t('回调地址'),
      dataIndex: 'redirect_uri',
      key: 'redirect_uri',
      render: (redirect_uri: string) => (
        <span>{redirect_uri}</span>
      ),
    },
    {
      title: t('操作'),
      dataIndex: 'op',
      key: 'op',
      width: 100,
      render: (_: string, platform_info: any) => (
        <>
        <Button type="text" icon={<Edit />} onClick={() => onEdit?.(platform_info)}/>
        <Button type="text" icon={<Trash />} onClick={() => onDelete?.(platform_info)}/>
        </>
      ),
    },
  ];
  return (
    <Table
      pagination={false}
      rowKey={(item: any) => item.scm_platform }
      dataSource={dataSource}
      columns={columns}
    />
  );
};


export default OAuthTable;
