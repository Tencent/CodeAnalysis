import React from 'react';
import { Link } from 'react-router-dom';
import { Table, Tooltip, Button, Tag } from 'coding-oa-uikit';
import Stop from 'coding-oa-uikit/lib/icon/Stop';
import Undo from 'coding-oa-uikit/lib/icon/Undo';

// 项目内
import { t } from '@src/i18n/i18next';
import EllipsisTemplate from '@src/components/ellipsis';
import { formatDateTime, getUserName } from '@src/utils';
import { getProjectTeamRouter } from '@src/utils/getRoutePath';

// 模块内
import { TEAM_STATUS_CHOICES, TEAM_STATUS_ENUM } from './constants';

const { Column } = Table;

interface IProps {
  dataSource: Array<any>;
  pagination: any;
  onDelete: (team: any) => void;
  onRecover: (team: any) => void;
}

const formatStatus = (status: any) => {
  const info = status === TEAM_STATUS_ENUM.ACTIVE ? {
    text: TEAM_STATUS_CHOICES[TEAM_STATUS_ENUM.ACTIVE],
    color: 'success',
  } : {
    text: TEAM_STATUS_CHOICES[TEAM_STATUS_ENUM.INACTIVE],
    color : 'red',
  };
  return (
    <Tag color={info.color}>{info.text}</Tag>
  );
};

const TeamTable = ({ dataSource, pagination, onDelete, onRecover }: IProps) => {
  return (
    <>
      <Table pagination={pagination} rowKey={(item: any) => item.id} dataSource={dataSource}>
        <Column
          title={t('项目名称')}
          dataIndex="status"
          render={(status: number, team: any) => (
            <>
              {status === TEAM_STATUS_ENUM.ACTIVE
              ? <Link to={getProjectTeamRouter(team.organization.org_sid, team.name)}>
                <EllipsisTemplate>{team.display_name}</EllipsisTemplate>
              </Link>
              : <EllipsisTemplate>{team.display_name}</EllipsisTemplate>
              }
              <div className="text-grey-6 fs-12 mt-sm">
                {team.name}
              </div>
            </>
          )}
        />
        <Column
          title={t('所属团队')}
          dataIndex="organization"
          render={(organization: any) => <EllipsisTemplate>{organization?.name}</EllipsisTemplate>}
        />
        <Column
          title={t('管理员')}
          dataIndex="admins"
          render={(admins: Array<any>) => admins.map((user: any) => getUserName(user)).join('; ')
          }
        />
        <Column
          title={t('创建时间')}
          dataIndex="created_time"
          render={(created_time: any) => formatDateTime(created_time)}
        />
        <Column
          title={t('状态')}
          dataIndex="status"
          render={(status: number) => formatStatus(status)}
        />
        <Column
          title={t('操作')}
          dataIndex="status"
          render={(status: number, team: any) => (
            <>
              {status === TEAM_STATUS_ENUM.ACTIVE && <Tooltip title={t('禁用团队')}>
                <Button
                  className="mr-sm"
                  shape="circle"
                  icon={<Stop />}
                  danger
                  onClick={() => onDelete(team)}
                />
              </Tooltip>}
              {status === TEAM_STATUS_ENUM.INACTIVE && <Tooltip title={t('恢复团队')}>
                <Button
                  className="mr-sm"
                  shape="circle"
                  icon={<Undo />}
                  onClick={() => onRecover(team)}
                />
              </Tooltip>}
            </>
          )}
        />
      </Table>
    </>
  );
};

export default TeamTable;
