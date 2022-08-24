import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import { useHistory } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { isEmpty, concat } from 'lodash';
import { Tabs, Input, Button, Spin, Divider } from 'coding-oa-uikit';

// 项目内
import { OrgStatusEnum, DEFAULT_TEAM_PAGER } from '@src/constant';
import { getProjectsRouter, getWorkspaceRouter } from '@src/utils/getRoutePath';
import Header from '@src/modules/layout/header';
import { getTeams } from '@src/services/team';
import TeamModal from './team-modal';
import TeamCard from './team-card';
import style from './style.scss';

const { Search } = Input;

const containerNode = document.getElementById('container');

const Team = () => {
  const [name, setName] = useState('');
  const [list, setList] = useState([]);
  const [pager, setPager] = useState(DEFAULT_TEAM_PAGER);
  const [visible, setVisible] = useState(false);
  const [data, setData] = useState();
  const [scrollLoading, setScrollLoading] = useState(true);
  const { count, pageStart, allLoaded } = pager;
  const INIT_LOAD_SIZE = 50;

  const history = useHistory();
  const { t } = useTranslation();

  useEffect(() => {
    getTeamList(false, DEFAULT_TEAM_PAGER.pageStart, INIT_LOAD_SIZE, {}, (list: any) => {
      // 用户进入团队页面，如果不存在团队，则默认弹出创建团队弹框
      if (isEmpty(list)) {
        setVisible(true);
      }
    });
  }, []);

  /** 获取团队列表 */
  const getTeamList = async (
    scroll = false,
    offset = pageStart,
    limit = DEFAULT_TEAM_PAGER.pageSize,
    searchParams = {},
    callback?: (list: any) => void,
  ) => {
    const { count, results }: any = (await getTeams({ offset, limit, ...searchParams })) || {};
    setScrollLoading(false);
    setPager({
      pageSize: limit,
      pageStart: offset + limit,
      count,
      allLoaded: offset + limit >= count,
    });
    if (scroll) {
      setList(concat(list, results || []));
    } else {
      setList(results || []);
    }
    callback?.(results);
  };

  /** 筛选 */
  const onSearch = (value: string) => {
    getTeamList(false, DEFAULT_TEAM_PAGER.pageStart, count, {
      name: value,
    });
  };

  /** 滚动加载更多团队 */
  const loadMoreTeam = () => {
    const teamWrapper = document.getElementById('team-wrapper');
    if (teamWrapper.scrollTop + teamWrapper.clientHeight > teamWrapper.scrollHeight * 0.8
      && !allLoaded && !scrollLoading) {
      setScrollLoading(true);
      getTeamList(true);
    }
  };

  /** 点击团队card */
  const onClickTeam = (data: any) => {
    if (data.status > OrgStatusEnum.ACTIVE) {
      // 团队未审核通过可弹框修改
      setData({
        ...data,
        apply_msg: data.last_perm_apply?.apply_msg ?? '',
      });
      setVisible(true);
    } else {
      if (data.repo_count) {
        // 存在分析任务则进入工作台
        history.push(getWorkspaceRouter(data.org_sid));
      } else {
        history.push({
          pathname: getProjectsRouter(data.org_sid),
          state: {
            // 用户从团队进入项目，如果不存在项目则默认弹出创建项目弹框
            visible: !data.team_count,
          },
        });
      }
    }
  };

  const onCreateFinish = () => {
    setPager(DEFAULT_TEAM_PAGER);
    getTeamList(false, DEFAULT_TEAM_PAGER.pageStart, INIT_LOAD_SIZE, {});
  };

  return (
    <>
      <Header />
      {containerNode && ReactDOM.createPortal(<div className={style.teamContainer}>
          <TeamModal
            visible={visible}
            data={data}
            onCancel={() => setVisible(false)}
            onOk={onCreateFinish}
          />
          <Tabs
            defaultActiveKey="all"
            size="large"
            tabBarExtraContent={
              <>
                <Search
                  allowClear
                  defaultValue={name}
                  value={name}
                  size="middle"
                  placeholder={t('团队名称')}
                  onChange={e => setName(e.target.value)}
                  onSearch={value => onSearch(value)}
                  style={{ width: 200 }}
                />
                <Button
                  className="ml-md"
                  type="primary"
                  onClick={() => {
                    setVisible(true);
                    setData(undefined);
                  }}
                >
                  {t('创建团队')}
                </Button>
              </>
            }
          >
            <Tabs.TabPane tab={t('所有团队')} key="all">
              <div
                className={style.teamWrapper}
                id='team-wrapper'
                onScroll={loadMoreTeam}
              >
                  {list.map((item: any) => (
                    <div
                      key={item.id}
                      className={style.team}
                      onClick={() => onClickTeam(item)}
                    >
                      <TeamCard data={item} />
                    </div>
                  ))}
                  <div style={{ textAlign: 'center' }}><Spin spinning={scrollLoading} /></div>
              </div>
              {!allLoaded && <Divider plain>{t('滚动加载更多团队')}</Divider>}
            </Tabs.TabPane>
          </Tabs>
        </div>, containerNode)}
    </>
  );
};

export default Team;
