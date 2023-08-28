import React from 'react';
import { t } from 'i18next';
import { Table, Button, Space, Popconfirm } from 'coding-oa-uikit';

// 项目内
import { AuthTypeEnum, AUTH_TYPE_CHOICES, ScmPlatformEnum, SCM_PLATFORM_CHOICES, SCM_PLATFORM_OPTIONS, SCM_PLATFORM_ICONS } from './constant';
import s from './style.scss';

const { Column } = Table;

interface AuthTableProps {
  /** 数据源 */
  dataSource: Array<any>;
  /** 编辑操作 */
  onEdit: (authinfo: any) => void;
  /** 删除操作 */
  onDel: (authinfo: any) => void;
  /** 是否展示凭证创建渠道，默认不展示 */
  showOrigin?: boolean;
}

const AuthTable = ({ dataSource, onEdit, onDel, showOrigin }: AuthTableProps) => <Table
    rowKey={(item: any) => `${item.auth_type}#${item.id}`}
    dataSource={dataSource}
    pagination={{
      hideOnSinglePage: true,
      pageSize: 30,
      showTotal: (total: number, range: [number, number]) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
    }}
  >
    <Column
      title={t('平台')}
      width={400}
      filters={SCM_PLATFORM_OPTIONS}
      onFilter={(value, record: any) => record.scm_platform === value}
      dataIndex='scm_platform'
      render={(value: ScmPlatformEnum) => <div className={s.platform}>
        <img src={SCM_PLATFORM_ICONS[value]} alt={SCM_PLATFORM_CHOICES[value]} className={s.icon}/>
        <div className={s.platformTitle}>{SCM_PLATFORM_CHOICES[value]}</div>
      </div>}
    />
    <Column
      title={t('凭证')}
      dataIndex='scm_username'
      render={(value: string, record: any) => {
        let txt: React.ReactNode = value;
        if (record.auth_type === AuthTypeEnum.SSH) {
          txt = record.name;
        }
        return <span className='text-weight-medium'>
          {AUTH_TYPE_CHOICES[record.auth_type as AuthTypeEnum]}：{txt}
          {showOrigin && <span className={s.origin}>(在 {record?.auth_origin || 'CodeDog'} 创建)</span>}
        </span>;
      }
      }
    />
    <Column
      title={t('操作')}
      dataIndex='op'
      width={300}
      render={(_, record: any) => <Space>
        <Button
          type="link"
          onClick={() => onEdit(record)}
        >
          编辑凭证
        </Button>
        <Popconfirm
          title="注意：删除凭证可能导致代码库分析失败"
          onConfirm={() => onDel(record)}
        >
          <Button type="link" danger>
            删除凭证
          </Button>
        </Popconfirm>
      </Space>}
    />
  </Table>;

export default AuthTable;
