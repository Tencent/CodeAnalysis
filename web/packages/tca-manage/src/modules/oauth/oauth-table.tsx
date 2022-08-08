import React from 'react';
import { useTranslation } from 'react-i18next';
import { get } from 'lodash';
import { Table, Tag, Space, PrimaryTableCol } from 'tdesign-react';

// 项目内
import s from '@src/modules/style.scss';
import { ScmPlatformEnum, SCM_PLATFORM_URL_PREFIX_CHOICES, SCM_PLATFORM_CHOICES } from '@plat/oauth';

// 模块内

import { OAuthSettingData } from './types';

interface OAuthTableProps {
  dataSource: OAuthSettingData[];
  onEdit: (platformInfo: OAuthSettingData, create: boolean) => void;
  onDelete: (platformInfo: OAuthSettingData) => void;
}

const OAuthTable = ({ dataSource, onEdit, onDelete }: OAuthTableProps) => {
  const { t } = useTranslation();

  const columns: PrimaryTableCol<OAuthSettingData>[] = [
    {
      title: t('平台'),
      colKey: 'scm_platform',
      width: 100,
      cell: ({ row }) => (
        <a
          className='link-name text-weight-bold'
          href={get(SCM_PLATFORM_URL_PREFIX_CHOICES, row.scm_platform, '') as string}
          target='_blank'
          rel="noopener noreferrer"
        >
          {SCM_PLATFORM_CHOICES[row.scm_platform as ScmPlatformEnum] || row.scm_platform_name}
        </a>
      ),
    },
    {
      title: t('平台描述'),
      colKey: 'scm_platform_desc',
      width: 240,
    },
    {
      title: t('配置状态'),
      colKey: 'client_id',
      width: 100,
      cell: ({ row }) => (
        row.client_id ? <Tag theme='success' variant='light'>{t('已配置')}</Tag> : <Tag>{t('未配置')}</Tag>
      ),
    },
    {
      title: t('操作'),
      colKey: 'op',
      width: 120,
      cell: ({ row }) => (
        row.client_id ? <Space breakLine>
          <a
            onClick={() => onEdit?.(row, false)}
          >
            {t('更新配置')}
          </a>
          <a
            onClick={() => onDelete?.(row)}
            className={s.deleteOp}
          >
            {t('删除配置')}
          </a>
        </Space> : <a
          onClick={() => onEdit?.(row, true)}
        >
          {t('创建配置')}
        </a>
      ),
    },
  ];

  return (
    <Table
      rowKey='scm_platform'
      data={dataSource}
      columns={columns}
    />
  );
};


export default OAuthTable;
