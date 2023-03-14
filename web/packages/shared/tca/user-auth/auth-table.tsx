import React from 'react';
import { t } from 'i18next';
import { Table, Button, Tag, Tooltip, Space, Popconfirm } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';
import Close2Icon from 'coding-oa-uikit/lib/icon/Close2';
import Success from 'coding-oa-uikit/lib/icon/Success';
import Aborted2 from 'coding-oa-uikit/lib/icon/Aborted2';

// 项目内
import { AuthTypeEnum, AUTH_TYPE_CHOICES, ScmPlatformEnum, SCM_PLATFORM_CHOICES, SCM_PLATFORM_OPTIONS } from './constant';

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
      title={t('凭证')}
      dataIndex='scm_username'
      render={(value: string, record: any) => {
        let txt: React.ReactNode = value;
        if (record.auth_type === AuthTypeEnum.OAUTH) {
          txt = record.oauth_status ? <>已认证 <Success /></> : <>未认证 <Aborted2 /></>;
        } else if (record.auth_type === AuthTypeEnum.SSH) {
          txt = record.name;
        }
        return <span className='text-weight-medium'>{AUTH_TYPE_CHOICES[record.auth_type as AuthTypeEnum]}：{txt}</span>;
      }
      }
    />
    <Column
      title={t('平台')}
      dataIndex='scm_platform'
      filters={SCM_PLATFORM_OPTIONS}
      onFilter={(value, record: any) => record.scm_platform === value}
      render={(value: ScmPlatformEnum) => <Tag>{SCM_PLATFORM_CHOICES[value]}</Tag>}
    />
    {showOrigin && <Column
      title={t('创建渠道')}
      dataIndex='auth_origin'
      render={(value: string) => value || 'CodeDog'}
    />}
    <Column
      title={t('操作')}
      dataIndex='op'
      render={(_, record: any) => {
        if (record.auth_type === AuthTypeEnum.OAUTH) {
          return !record.oauth_status ? <Tooltip title="去授权"><Button type="text" icon={<LinkIcon />} onClick={() => onEdit(record)} /></Tooltip> : <Space>
            <Tooltip title="重新授权"><Button type="text" icon={<RefreshIcon />} onClick={() => onEdit(record)} /></Tooltip>
            <Popconfirm
              title="确定取消授权？"
              onConfirm={() => onDel(record)}
            >
              <Button type="text" icon={<Close2Icon />} />
            </Popconfirm>
          </Space>;
        }
        return <Space>
          <Tooltip title="编辑凭证">
            <Button
              type="text"
              icon={<Edit />}
              onClick={() => onEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="确定移除该凭证？"
            onConfirm={() => onDel(record)}
          >
            <Button type="text" icon={<Trash />} />
          </Popconfirm>
        </Space>;
      }}
    />
  </Table>;

export default AuthTable;
