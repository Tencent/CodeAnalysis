import React from 'react';
import { useTranslation } from 'react-i18next';
import { Table, Button, Tag, Tooltip } from 'coding-oa-uikit';
import Edit from 'coding-oa-uikit/lib/icon/Edit';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';
import Close2Icon from 'coding-oa-uikit/lib/icon/Close2';
import { useStateStore } from '@tencent/micro-frontend-shared/hook-store';

// 项目内
import { getNickName } from '@src/utils';
import { NAMESPACE, UserState } from '@src/store/user';
import { AUTH_TYPE_CHOICES, AuthTypeEnum, SCM_PLATFORM_CHOICES, ScmPlatformEnum } from '@src/constant';

const { Column } = Table;

interface AuthTableProps {
  /** 数据源 */
  dataSource: Array<any>;
  /** 编辑操作 */
  onEdit: (authinfo: any) => void;
  /** 删除操作 */
  onDel: (authinfo: any) => void;
  /** 是否展示平台，默认展示 */
  showPlatform?: boolean;
  /** 是否展示凭证创建渠道，默认不展示 */
  showOrigin?: boolean;
}

const AuthTable = ({ dataSource, onEdit, onDel, showPlatform = true, showOrigin = false }: AuthTableProps) => {
  const { t } = useTranslation();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);

  return (
    <Table
      rowKey={(item: any) => `${item.auth_type}#${item.id}`}
      dataSource={dataSource}
      pagination={{
        showTotal: (total: number, range: [number, number]) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
      }}
    >
      {showPlatform && <Column
        title={t('平台')}
        dataIndex='scm_platform'
        render={(value: ScmPlatformEnum) => SCM_PLATFORM_CHOICES[value]}
      />}
      <Column
        title={t('凭证')}
        dataIndex='scm_username'
        render={(value: string, record: any) => {
          const authType = AUTH_TYPE_CHOICES[record.auth_type as AuthTypeEnum];
          let txt = value;
          if (record.auth_type === AuthTypeEnum.OAUTH) {
            txt = record.oauth_status ? getNickName(userinfo) : '未认证';
          }
          if (record.auth_type === AuthTypeEnum.SSH) {
            txt = record.name;
          }
          return <Tag className='text-weight-medium'>{authType}: {txt}</Tag>;
        }
        }
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
            return !record.oauth_status ? <Tooltip title="去授权"><Button type="text" icon={<LinkIcon />} onClick={() => onEdit(record)} /></Tooltip> : <>
              <Tooltip title="重新授权"><Button type="text" icon={<RefreshIcon />} onClick={() => onEdit(record)} /></Tooltip>
              <Tooltip title="取消授权"><Button type="text" icon={<Close2Icon />} onClick={() => onDel(record)} /></Tooltip>
            </>;
          }
          return <>
            <Tooltip title="编辑凭证">
              <Button
                type="text"
                icon={<Edit />}
                onClick={() => onEdit(record)}
              />
            </Tooltip>
            <Tooltip title="移除凭证">
              <Button type="text" icon={<Trash />} onClick={() => onDel(record)} />
            </Tooltip>
          </>;
        }}
      />
    </Table>
  );
};

export default AuthTable;
