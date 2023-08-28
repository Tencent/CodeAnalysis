import React, { useState } from 'react';
import { get } from 'lodash';
import { t } from '@src/utils/i18n';
import { DialogPlugin, MessagePlugin } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { getTeams, putTeamStatus } from '@src/services/teams';

// 模块内
import { TEAM_FILTER_FIELDS as filterFields, TEAM_SEARCH_FIELDS, TeamStateEnum } from './constants';
import ProjectTeamTable from './team-table';
import { DeleteModal } from '@tencent/micro-frontend-shared/tdesign-component/modal';

const ProjectTeams = () => {
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getTeams, [filter]);
  const { results: listData = [], count = 0 } = data || {};
  const [deleteVisible, setDeleteVisible] = useState<boolean>(false);
  const [curTeam, setCurTeam] = useState<any>(null);

  // 禁用项目
  const onDeleteTeam = (team: any) => {
    setDeleteVisible(true);
    setCurTeam(team);
  };

  const handleDeleteTeam = () => {
    putTeamStatus(get(curTeam, ['organization', 'org_sid']), get(curTeam, 'name'), { status: TeamStateEnum.INACTIVE }).then(() => {
      MessagePlugin.success(t('已禁用项目'));
      reload();
      setDeleteVisible(false);
      setCurTeam(null);
    });
  };

  // 恢复团队
  const onRecoverTeam = (team: any) => {
    const confirmDia = DialogPlugin.confirm({
      header: t('恢复项目'),
      body: t('确定要恢复已禁用的项目吗？'),
      onConfirm() {
        putTeamStatus(get(team, ['organization', 'org_sid']), get(team, 'name'), { status: TeamStateEnum.ACTIVE }).then(() => {
          MessagePlugin.success(t('已恢复项目'));
          confirmDia.hide();
          reload();
        });
      },
      onClose() {
        confirmDia.hide();
      },
    });
  };

  return (
    <>
      <PageHeader title={t('项目列表')} description="平台各团队创建的项目列表" />
      <Search fields={TEAM_SEARCH_FIELDS} loading={false} searchParams={searchParams} />
      <div className="px-lg">
        <ProjectTeamTable
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
          loading={isLoading}
          onDelete={onDeleteTeam}
          onRecover={onRecoverTeam}
        />
      </div>
      <DeleteModal
        actionType={t('禁用')}
        objectType={t('项目')}
        confirmName={curTeam?.name}
        visible={deleteVisible}
        onCancel={() => setDeleteVisible(false)}
        onOk={handleDeleteTeam}
      />
    </>
  );
};

export default ProjectTeams;
