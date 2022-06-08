// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { Tabs, Button, Input } from 'coding-oa-uikit';
import { filter } from 'lodash';

import { getProjects } from '@src/services/team';
import List from './list';
import Modal from './modal';
import style from './style.scss';

const { TabPane } = Tabs;

const Projects = () => {
  const { orgSid }: any = useParams();
  const history: any = useHistory();
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<any>([]);
  const [manageData, setManageData] = useState<any>([]);
  const [tab, setTab] = useState<string>('all');
  const [projectName, setProjectName] = useState<string>('');
  const [visible, setVisible] = useState<boolean>(false);

  useEffect(() => {
    getListData();
  }, [orgSid, tab, projectName]);

  useEffect(() => {
    // 用户从团队进入项目，如果不存在项目则默认弹出创建项目弹框
    if (history.location.state?.visible) {
      setVisible(true);
    }
  }, [history.location.state]);

  const getListData = () => {
    const params: any = {};
    if (tab === 'manage') params.scope = 1;
    if (projectName) params.display_name = projectName;

    setLoading(true);
    getProjects(orgSid, { ...params }).then((res) => {
      // 只显示未禁用的项目
      const activeProjects = filter(res, {status: 1});
      tab === 'manage' ? setManageData(activeProjects) : setData(activeProjects);
    })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <>
      <Tabs
        activeKey={tab}
        onChange={(value: any) => setTab(value)}
        className={style.projects}
        tabBarExtraContent={(
          <div className={style.searchBar}>
            <Input.Search
              placeholder="项目名称"
              size='middle'
              className={style.search}
              onSearch={value => setProjectName(value)}
            />
            <Button type='primary' onClick={() => setVisible(true)}>创建项目</Button>
          </div>
        )}
      >
        <TabPane tab="项目" disabled key="null" />

        <TabPane tab="所有项目" key="all">
          <List
            orgSid={orgSid}
            loading={loading}
            data={data}
          />
        </TabPane>
        <TabPane tab="我管理的" key="manage">
          <List
            orgSid={orgSid}
            loading={loading}
            data={manageData}
          />
        </TabPane>
      </Tabs>
      <Modal
        orgSid={orgSid}
        visible={visible}
        onClose={() => setVisible(false)}
        callback={() => getListData()}
      />
    </>
  );
};

export default Projects;
