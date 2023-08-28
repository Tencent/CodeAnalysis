import React from 'react';
import classnames from 'classnames';
import { t } from '@src/utils/i18n';
import { PaginationProps, Tag, Space } from 'tdesign-react';

import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';

import { LibTypeEnum, LIB_TYPE_CHOICES, LIB_ENV_CHOICES, LibData } from '@src/constant';
import style from './style.scss';

interface TableProps {
  loading: boolean;
  dataSource: LibData[];
  pagination: PaginationProps;
  opCell: (row: LibData) => React.ReactNode
}

const ToolLibTable = ({ loading, dataSource, pagination, opCell }: TableProps) => (
  <Table
    loading={loading}
    data={dataSource}
    pagination={pagination}
    columns={[{
      colKey: 'name',
      title: t('依赖名称'),
      width: 200,
      fixed: 'left',
      cell: ({ row }) => (
        <>
          <p className='tca-text-weight-bold'>{row.name}</p>
          {row.description && <p className='tca-fs-12 tca-mt-sm tca-text-grey-6'>{row.description}</p>}
        </>
      ),
    }, {
      colKey: 'envs',
      title: t('环境变量'),
      width: 300,
      cell: ({ row }) => (
        <code>
          {
            Object.entries(row.envs).map(([key, value]) => (
              <p className={style.envs} key={key}>{key} = {value}</p>
            ))
          }
        </code>
      ),
    }, {
      colKey: 'lib_os',
      title: t('适用系统'),
      width: 120,
      cell: ({ row }) => (
        <Space size={8} align='center' breakLine>
          {row.os.map(os => (
            <Tag key={os}>{LIB_ENV_CHOICES[os]}</Tag>
          ))}
        </Space>
      ),
    }, {
      colKey: 'lib_type',
      title: t('类型'),
      width: 120,
      cell: ({ row }) => (
        <div className={style.lib}>
          <Tag className={classnames(style.libTag, { [style.privite]: row.lib_type === LibTypeEnum.PRIVATE })}
          >{LIB_TYPE_CHOICES[row.lib_type] || row.lib_type}</Tag>
        </div>
      ),
    }, {
      colKey: 'created_time',
      title: t('创建时间'),
      width: 180,
      cell: ({ row }) => (
        <div style={{ minWidth: '150px' }}>{formatDateTime(row.created_time)}</div>
      ),
    }, {
      colKey: 'modified_time',
      title: t('更新时间'),
      width: 180,
      cell: ({ row }) => formatDateTime(row.modified_time) || '- -',
    }, {
      colKey: 'creator.nickname',
      title: t('负责人'),
      width: 150,
    }, {
      colKey: 'id',
      title: t('操作'),
      width: 100,
      fixed: 'right',
      cell: ({ row }) => opCell(row),
    }]}
  />
);

export default ToolLibTable;
