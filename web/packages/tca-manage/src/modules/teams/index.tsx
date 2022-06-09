import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Row, Col, Tabs, Modal, message } from 'coding-oa-uikit';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useURLParams, useDeepEffect } from '@src/utils/hooks';
import { getTeams, putTeamStatus } from '@src/services/teams';
import DeleteModal from '../components/delete-modal';

// 模块内
import s from './style.scss';
import Search from './search';
import TeamTable from './team-table';
import { TEAM_STATUS_ENUM } from './constants';

const { TabPane } = Tabs;
const { confirm } = Modal;

const FILTER_FIELDS = ['status', 'organization_name', 'display_name', 'organization_sid'];

const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

const Teams = () => {
  const history = useHistory();
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState(false);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);
  const [deleteVisible, setDeleteVisible] = useState<boolean>(false);
  const [curTeam, setCurTeam] = useState<any>(null);
  const [reload, setReload] = useState<boolean>(false);

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    setLoading(true);
    getTeams(filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
      setLoading(false);
    });
  };

  // 当路由参数变化时触发
  useDeepEffect(() => {
    getListData();
  }, [filter]);

  // 手动触发
  useEffect(() => {
    getListData();
  }, [reload]);  

  // 筛选
  const onSearch = (params: any) => {
    history.push(customFilterURLPath({
      limit: DEFAULT_PAGER.pageSize,
      offset: DEFAULT_PAGER.pageStart,
      ...params,
    }));
  };

  // 翻页
  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  // 禁用项目
  const onDeleteTeam = (team: any) => {
    setDeleteVisible(true);
    setCurTeam(team);
  };

  const handleDeleteTeam = () => {
    putTeamStatus(get(curTeam,['organization', 'org_sid']), get(curTeam, 'name'), {status: TEAM_STATUS_ENUM.INACTIVE}).then(() => {
      message.success('已删除项目');
      setReload(!reload);
      setDeleteVisible(false);
      setCurTeam(null);
    });
  };

  // 恢复团队
  const onRecoverTeam = (team: any) => {
    confirm({
      title: '恢复团队',
      content: '确定要恢复团队吗？',
      onOk() {
        putTeamStatus(get(team,['organization', 'org_sid']), get(team, 'name'), {status: TEAM_STATUS_ENUM.ACTIVE}).then(() => {
          message.success('已恢复项目');
          setReload(!reload);
        });
      },
      onCancel() {},
    });
  };

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="project" size="large">
            <TabPane tab={t('项目列表')} key="project" />
          </Tabs>
        </Col>
      </Row>
      <div className={s.filterContent}>
        <Search loading={loading} searchParams={searchParams} callback={onSearch} />
      </div>
      <div className="px-lg">
        <TeamTable
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
            onChange: onChangePageSize,
          }}
          onDelete={onDeleteTeam}
          onRecover={onRecoverTeam}
        />
      </div>
      <DeleteModal
        deleteType={t('项目')}
        confirmName={curTeam?.name}
        visible={deleteVisible}
        onCancel={() => setDeleteVisible(false)}
        onOk={handleDeleteTeam}
      />
    </>
  );
};

export default Teams;
