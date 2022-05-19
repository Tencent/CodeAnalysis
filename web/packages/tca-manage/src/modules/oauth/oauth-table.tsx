import React from 'react';
import { Table, Button, Tag } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import Plus from 'coding-oa-uikit/lib/icon/Plus';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';

// 模块内
import { SCM_PLATFORM } from './constants';

interface IProps {
  dataSource: Array<any>;
  onEdit: (platform_info: any, create: boolean) => void;
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
      render: (scm_platform_desc: string) => (
        <span>{scm_platform_desc}</span>
      ),
    },
    {
      title: t('配置状态'),
      dataIndex: 'client_id',
      key: 'client_id',
      render: (client_id: string) => (
        client_id ? <Tag color='success'>已配置</Tag> : <Tag color='default'>未配置</Tag>
      ),
    },
    {
      title: t('操作'),
      dataIndex: 'op',
      key: 'op',
      width: 100,
      render: (_: string, platform_info: any) => (
        platform_info?.client_id ? <>
        <Button type="text" icon={<Edit/>} onClick={() => onEdit?.(platform_info, false)}/>
        <Button type="text" icon={<Trash />} onClick={() => onDelete?.(platform_info)}/>
        </> : <>
        <Button type="text" icon={<Plus />} onClick={() => onEdit?.(platform_info, true)}/>
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
