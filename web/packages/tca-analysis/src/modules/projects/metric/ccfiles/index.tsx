// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果 - 圈复杂度 - 文件列表页
 *
 */
import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { cloneDeep, toNumber, omit, omitBy } from 'lodash';
import qs from 'qs';

import { Table, Avatar } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/constant';
import { getProjectRouter, getProjectBlankRouter } from '@src/utils/getRoutePath';
import { getCCFilesIssues } from '@src/services/projects';
import { CC_CHANGE_TYPE_CHOICES } from '../../constants';
import Search from './search';

import style from './style.scss';

const { Column } = Table;

interface CCFilesProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
}

const CCFiles = (props: CCFilesProps) => {
  const history = useHistory();
  const { orgSid, teamName, repoId, projectId } = props;
  const [filesIssue, setFilesIssue] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;

  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getListData(pageStart, pageSize, {
      ...searchParams,
    });
  }, [projectId]);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };

    setLoading(true);
    getCCFilesIssues(orgSid, teamName, repoId, projectId, params)
      .then((response: any) => {
        setCount(response.count);
        history.push(`${location.pathname}?${qs.stringify(params)}`);
        setFilesIssue(response.results || []);
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
    <div className={style.ccfiles}>
      <Search
        href={`${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/ccissues`}
        searchParams={cloneDeep(searchParams)}
        loading={loading}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      {/* <div className={commonStyle.bottom}>
        <TableSearchTop tab="ccfiles" />
      </div> */}
      <Table
        dataSource={filesIssue}
        rowKey={(item: any) => item.id}
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
          title="所属文件"
          dataIndex="file_path"
          render={(file_path, data: any) => (
            <a
              target="_blank"
              href={`${getProjectBlankRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
              )}/metric/ccfiles/${data.id}`}
              className="link-name"
              title={data.file_path} rel="noreferrer"
            >
              <p>{file_path.split('/').pop()}</p>
              <p className="path">{file_path}</p>
            </a>
          )}
        />
        <Column
          title="文件内方法变更类型"
          dataIndex="change_type"
          width={180}
          align='center'
          render={change_type => (
            // todo: remove
            <span
              style={{
                color: CC_CHANGE_TYPE_CHOICES[change_type].labelColor,
              }}
            >
              {CC_CHANGE_TYPE_CHOICES[change_type].label}
            </span>
          )}
        />
        <Column
          title="超标方法圈复杂度总和"
          dataIndex="over_func_cc"
          width={180}
          align='center'
        />
        <Column
          title="超标方法平均圈复杂度"
          dataIndex="over_cc_avg"
          width={180}
          align='center'
        />
        <Column
          title="超标方法个数"
          dataIndex="over_cc_func_count"
          width={180}
          align='center'
        />
        <Column
          title="最近修改人"
          dataIndex="last_modifier"
          render={last_modifier => (
            <>
              <Avatar size={24} icon={<UserIcon />} /> {last_modifier}
            </>
          )}
        />
      </Table>
    </div>
  );
};
export default CCFiles;
