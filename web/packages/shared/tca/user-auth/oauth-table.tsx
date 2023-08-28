import React from 'react';
import { t } from 'i18next';
import { Table, Button, Tag, Space, Popconfirm } from 'coding-oa-uikit';
import Success from 'coding-oa-uikit/lib/icon/Success';
import Aborted2 from 'coding-oa-uikit/lib/icon/Aborted2';

// 项目内
import { ScmPlatformEnum, SCM_PLATFORM_CHOICES, SCM_PLATFORM_ICONS } from './constant';
import s from './style.scss';

const { Column } = Table;

interface OauthTableProps {
  /** 数据源 */
  dataSource: Array<any>;
  /** 编辑操作 */
  onEdit: (authinfo: any) => void;
  /** 删除操作 */
  onDel: (authinfo: any) => void;
}

const OauthTable = ({ dataSource, onEdit, onDel }: OauthTableProps) => (
  <Table
    rowKey={(item: any) => `${item.auth_type}#${item.id}`}
    dataSource={dataSource}
    pagination={false}
  >
    <Column
      title={t('平台')}
      dataIndex='scm_platform'
      width={400}
      render={(value: ScmPlatformEnum) => <div className={s.platform}>
        <img src={SCM_PLATFORM_ICONS[value]} alt={SCM_PLATFORM_CHOICES[value]} className={s.icon}/>
        <div className={s.platformTitle}>{SCM_PLATFORM_CHOICES[value]}</div>
      </div>}
    />
    <Column
      title={t('状态')}
      dataIndex='oauth_status'
      render={(oauth_status: boolean) => (oauth_status
        ? <Tag icon={<Success />} color='green'>已认证</Tag>
        : <Tag icon={<Aborted2 />}>未认证</Tag>)
      }
    />
    <Column
      title={t('操作')}
      dataIndex='op'
      width={300}
      render={(_, record: any) => (!record.oauth_status
        ? <Button type="link" onClick={() => onEdit(record)}>前往认证</Button>
        : <Space>
        <Button type="link" onClick={() => onEdit(record)}>
          刷新认证
        </Button>
        <Popconfirm
          title="注意：取消认证可能导致代码库分析失败"
          onConfirm={() => onDel(record)}
        >
          <Button type="link" danger>
            取消认证
          </Button>
        </Popconfirm>
      </Space>)}
    />
  </Table>
);

export default OauthTable;
