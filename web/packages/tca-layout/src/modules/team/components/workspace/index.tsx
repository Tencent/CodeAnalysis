// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import { useParams, Link } from 'react-router-dom';
import { Tabs, Table } from 'coding-oa-uikit';
import AlignLeft from 'coding-oa-uikit/lib/icon/AlignLeft';
import Clock from 'coding-oa-uikit/lib/icon/Clock';
import { filter } from 'lodash';

import { DEFAULT_PAGER } from '@src/common/constants';
import { formatDateTime } from '@src/utils/index';
import { getRepoRouter, getRepoProjectRouter } from '@src/utils/getRoutePath';
import { getTeamRepos } from '@src/services/team';

import style from './style.scss';

const { Column } = Table;
const { TabPane } = Tabs;

const Workspace = () => {
  const { orgSid }: any = useParams();
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageSize, pageStart } = pager;

  useEffect(() => {
    getListData(pageStart, pageSize);
  }, [orgSid]);

  const getListData = (offset: number, limit: number) => {
    setLoading(true);
    getTeamRepos(orgSid, { offset, limit })
      .then((response) => {
        setPager({
          pageSize: limit,
          pageStart: offset,
          count: response.count,
        });
        const activeTeamRepos = filter(response?.results, ['project_team.status',1]);
        setList(activeTeamRepos || []);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  return (
    <Tabs activeKey={'repos'} className={style.workspace}>
      <TabPane tab="工作台" disabled key="null" />
      <TabPane tab="代码分析" key="repos">
        <Table
          loading={loading}
          dataSource={list}
          rowKey={(item: any) => item.id}
          className={style.repoList}
          pagination={{
            size: 'default',
            current: Math.floor(pageStart / pageSize) + 1,
            total: count,
            pageSize,
            showSizeChanger: true,
            showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
            onChange: onChangePageSize,
            onShowSizeChange,
          }}
        >
          <Column
            title="代码库"
            dataIndex="name"
            key="name"
            render={(name: string, record: any) => (
              <>
                <Link
                  className={cn('link-name', style.repoName)}
                  to={getRepoRouter(
                    record.project_team?.org_sid,
                    record.project_team?.name,
                    record.id,
                  )}
                >
                  {name}
                </Link>
                <p className={style.repoUrl}>{record.scm_url}</p>
              </>
            )}
          />
          <Column title="分支数量" dataIndex="branch_count" key="branch_count" />
          <Column title="分析次数" dataIndex="job_count" key="job_count" />
          <Column
            title="最近活跃分支"
            dataIndex="recent_active"
            key="recent_active"
            render={(recent_active: any, record: any) => {
              if (recent_active) {
                const {
                  id,
                  branch_name: branchName,
                  total_line_num: totalLineNum,
                  active_time: activeTime,
                } = recent_active;
                return (
                  <>
                    <div>
                      <Link
                        to={getRepoProjectRouter(
                          record.project_team?.org_sid,
                          record.project_team?.name,
                          record.id,
                          id,
                        )}
                      >
                        {branchName}
                      </Link>
                    </div>
                    <div className=" fs-12 text-grey-7">
                      {
                        activeTime && (
                          <span><Clock className="text-grey-6" /> {formatDateTime(activeTime)} &nbsp;</span>
                        )
                      }
                      {
                        totalLineNum && (
                          <span><AlignLeft /> {totalLineNum} 行 </span>
                        )
                      }
                    </div>
                  </>
                );
              }
              return '暂无分析记录';
            }}
          />
          <Column
            title="创建时间"
            dataIndex="created_time"
            key="created_time"
            render={time => time && formatDateTime(time)}
          />
        </Table>
      </TabPane>
    </Tabs>
  );
};

export default Workspace;
