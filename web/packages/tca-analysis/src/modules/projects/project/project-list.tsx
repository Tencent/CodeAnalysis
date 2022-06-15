// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      分支项目列表
 * author           luochunlan@coding.net
 * create at        2020-10-23
 */

import React, { useEffect, useState } from 'react';
import { Link, useHistory, useParams } from 'react-router-dom';
import { Table, Tooltip, Button, Input, Menu, Dropdown, message } from 'coding-oa-uikit';
import { pickBy, isNumber, get, toNumber, find } from 'lodash';
import qs from 'qs';
import { useSelector } from 'react-redux';

import SelectDropdown from '../../../components/select-dropdown';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';
import EllipsisH from 'coding-oa-uikit/lib/icon/EllipsisH';

import { useStateStore } from '@src/context/store';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useQuery } from '@src/utils/hooks';
import { getProjectRouter, getSchemeRouter } from '@src/utils/getRoutePath';
import { getProjects, delProject } from '@src/services/projects';
import { getMembers } from '@src/services/common';

import ScanModal from './scan-modal';
import NewProjectModal from './new-project-modal';
import DeleteModal from '@src/components/delete-modal';

import style from '../style.scss';

const { Column } = Table;

interface ProjectListProps {
  location?: any;
  params?: any;
  schemes: any;
  templates: any;
}

const ProjectList = (props: ProjectListProps) => {
  const { schemes = [], templates } = props;
  const { curRepo } = useStateStore();
  const history = useHistory();
  const query = useQuery();
  const { repoId = curRepo.id, org_sid: orgSid, team_name: teamName } = useParams() as any;

  const [list, setList] = useState([]);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const [visible, setVisible] = useState(false);
  const [projectId, setProjectId] = useState() as any;
  const [createProjectVsb, setCreateProjectVsb] = useState(false);
  const [curProjId, setCurProjId] = useState<number>(null);
  const [reload, setReload] = useState<boolean>(false);

    // 判断是否有权限删除分支项目
    const APP = useSelector((state: any) => state.APP);
    const isSuperuser = get(APP, 'user.is_superuser', false); // 当前用户是否是超级管理员
    const userName = get(APP, 'user.username', null);
    const [admins, setAdmins] = useState<any>([]);
    const isAdmin = !!find(admins, { username: userName });  // 当前用户是否是代码库管理员
    const deletable = isAdmin || isSuperuser;  // 删除权限
    const [deleteVisible, setDeleteVisible] = useState<boolean>(false);

  const [searchParams, setSearchParams] = useState({
    scan_scheme: query.get('scan_scheme') || '',
    branch_or_scheme: query.get('branch_or_scheme') || '',
  });

  const { pageSize, pageStart, count } = pager;

  useEffect(() => {
    repoId && getListData();
  }, [
    repoId,
    pager.pageSize,
    pager.pageStart,
    searchParams.scan_scheme,
    searchParams.branch_or_scheme,
    reload,
  ]);

  useEffect(() => {
    // 获取代码库成员
    if (repoId) {
      getMembers(orgSid, teamName, repoId).then((response) => {
        setAdmins(response.admins);
      });
    }
  }, [repoId]);

  const getListData = (limit: number = pageSize, offset: number = pageStart) => {
    const params = {
      limit,
      offset,
      ...pickBy(
        searchParams,
        (value, key) => isNumber(value) || (key === 'branch_or_scheme' && value),
      ),
    };
    getProjects(orgSid, teamName, repoId, {
      ...params,
      scan_scheme__status: 1,
    }).then((response) => {
      history.push(`${location.pathname}?${qs.stringify(params)}`);
      setList(response.results);
      setPager({ ...pager, count: response.count });
    });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    setPager({
      ...pager,
      pageStart: (page - 1) * pageSize,
    });
  };

  const onChangeSearchParams = (type: string, value: any) => {
    setSearchParams({
      ...searchParams,
      [type]: value,
    });

    setPager(DEFAULT_PAGER);
  };

  const onDeleteProject = (id: number) => {
    setCurProjId(id);
    setDeleteVisible(true);
  };
  
  const handleDeleteProject = () => {
    delProject(orgSid, teamName, repoId, curProjId).then(() => {
      message.success('已删除分支项目');
      setReload(!reload);
    }).finally(() => {
      setDeleteVisible(false);
      setCurProjId(null);
    });
  };

  return (
    <div className={style.projectList}>
      <div className={style.projectSearch}>
        <h3 className={style.title}>
          分支项目列表
            <Tooltip title="分支项目 = 分支 + 分析方案">
            <QuestionCircle className={style.icon} />
          </Tooltip>
        </h3>
        <SelectDropdown
          allowClear
          label='分析方案'
          dropdownStyle={{ marginRight: 10 }}
          selectedKeys={searchParams.scan_scheme && searchParams.scan_scheme !== 'all' ? [searchParams.scan_scheme] : []}
          onSelect={(e: any) => onChangeSearchParams('scan_scheme', toNumber(e.key))}
          data={schemes.map((item: any) => ({ text: item.name, value: item.id }))}
          onClear={() => onChangeSearchParams('scan_scheme', 'all')}
        />
        <Input.Search
          size='middle'
          style={{ width: 200 }}
          placeholder="分支/分析方案"
          value={searchParams.branch_or_scheme}
          onChange={(e: any) => {
            onChangeSearchParams('branch_or_scheme', e.target.value);
          }}
        />
        <Button
          style={{ float: 'right' }}
          type="primary"
          onClick={() => setCreateProjectVsb(true)}
        >
          添加分支项目
        </Button>
      </div>
      <Table
        size="small"
        dataSource={list}
        rowKey={(item: any) => item.id}
        pagination={{
          size: 'default',
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: false,
          showTotal: (total, range) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
          onChange: onChangePageSize,
        }}
      >
        <Column
          title="分支项目 ID"
          dataIndex="id"
          render={(id: number) => (
            <Link
              className={style.linkName}
              to={`${getProjectRouter(orgSid, teamName, repoId, id)}/overview`}
            >
              {id}
            </Link>
          )}
        />
        <Column title="分支名称" dataIndex="branch" />
        <Column
          title="分析方案"
          dataIndex={['scan_scheme', 'name']}
          render={(name, data: any) => (
            <Link
              className={style.linkName}
              target="_blank"
              to={`${getSchemeRouter(orgSid, teamName, repoId, get(data, 'scan_scheme.id'))}`}
            >
              {name}
            </Link>
          )}
        />

        <Column
          title="操作"
          dataIndex="id"
          width={240}
          render={ id => {
            const menu = (
              <Menu>
                <Menu.Item>
                  <a
                    onClick={() => {
                      setProjectId(id);
                      setVisible(true);
                    }}
                  >
                    启动分析
                  </a>
                </Menu.Item>
                <Menu.Item>
                  <Link
                    to={`${getProjectRouter(orgSid, teamName, repoId, id)}/overview`}
                  >
                    分支概览
                  </Link>
                </Menu.Item>
                <Menu.Item>
                  <Link
                    to={`${getProjectRouter(orgSid, teamName, repoId, id)}/scan-history`}
                  >
                    分析历史
                  </Link>
                </Menu.Item>
                {deletable && <Menu.Item>
                  <a
                    style={{color: 'red'}}
                    onClick={() => onDeleteProject(id)}
                  >
                    删除项目
                  </a>
                </Menu.Item>}
              </Menu>
            );
            return (
              <Dropdown overlay={menu} trigger={['click']}>
                <span className={style.linkName}>
                  <EllipsisH />
                </span>
              </Dropdown>
            );
          }
          }
        />
      </Table>
      <ScanModal
        orgSid={orgSid}
        teamName={teamName}
        visible={visible}
        repoId={repoId}
        projectId={projectId}
        onClose={() => setVisible(false)}
      />
      <NewProjectModal
        orgSid={orgSid}
        teamName={teamName}
        repoId={repoId}
        schemes={schemes}
        templates={templates}
        visible={createProjectVsb}
        onClose={() => setCreateProjectVsb(false)}
        callback={() => {
          getListData(DEFAULT_PAGER.pageStart);
          // getSchemes(branch);
        }}
      />
      <DeleteModal
        actionType='删除'
        objectType='分支项目'
        confirmName={`${curProjId}`}
        visible={deleteVisible}
        onCancel={() => setDeleteVisible(false)}
        onOk={handleDeleteProject}
      />
    </div>
  );
};

export default ProjectList;
