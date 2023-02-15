// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果 - 圈复杂度 - 方法列表页
 */
import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { cloneDeep, toNumber, omit, omitBy, findIndex } from 'lodash';
import qs from 'qs';

import { Table, Avatar } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/constant';
import { getProjectRouter } from '@src/utils/getRoutePath';
import { getCCFunIssues } from '@src/services/projects';
import { CC_CHANGE_TYPE_CHOICES } from '../../constants';

import Search from './search';
import IssueModal from './issue-modal';
import style from './style.scss';

const { Column } = Table;

interface CCIssuesProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
}

const CCIssues = (props: CCIssuesProps) => {
  const history = useHistory();
  const { orgSid, teamName, repoId, projectId } = props;
  const [data, setData] = useState<any>({
    list: [],
    next: null,
    previous: null,
  });
  const { list, next, previous } = data;

  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [issueModal, setIssueModal] = useState<any>({
    visible: false,
    issueId: null,
    isFirstIssue: false,  // 是否为第一个问题
    isLastIssue: false,  // 是否为最后一个问题
  });
  const { issueId } = issueModal;

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;

  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getListData(pageStart, pageSize, {
      ...searchParams,
    });
  }, [projectId]);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams, callback?: any) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };

    setLoading(true);
    getCCFunIssues(orgSid, teamName, repoId, projectId, params)
      .then((response: any) => {
        setCount(response.count);
        callback?.(response.results || []);
        history.replace(`${location.pathname}?${qs.stringify(params)}`);
        setData({
          list: response.results || [],
          next: response.next,
          previous: response.previous,
        });
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

  useEffect(() => {
    // 弹框显示的 Issue，设置行背景
    // if (issueId && issueModal.visible) {
    //   $(`tr[data-row-key!=${issueId}] td`).css('background-color', 'transparent');
    //   $(`tr[data-row-key=${issueId}] td`).css('background-color', '#f5f7fa')
    // }

    if (issueModal.visible) {
      getIssueBoundary();
    }
  }, [issueModal.visible, issueId]);

  // 判断当前 Issue 是否为第一个/最后一个问题
  const getIssueBoundary = () => {
    const index = findIndex(list, { id: issueId });
    const issueStatus = {
      isFirstIssue: false,
      isLastIssue: false,
    };

    if (index === 0 && !previous) {  // 第一个问题
      issueStatus.isFirstIssue = true;
    }
    if (index === list.length - 1 && !next) { // 最后一个问题
      issueStatus.isLastIssue = true;
    }
    setIssueModal({ ...issueModal, ...issueStatus });
  };

  // Issue 弹框 - 上一个问题
  const prevIssue = () => {
    const index = findIndex(list, { id: issueId });
    if (index === 0) {
      if (previous) {  // 当前页的第一个问题，需列表请求前一页，取前一页的最后一个 issue 展示
        getListData(pageStart - pageSize, pageSize, searchParams, (data: any) => {
          setIssueModal({
            ...issueModal,
            issueId: data[data.length - 1]?.id,
          });
        });
      }
    } else {
      setIssueModal({
        ...issueModal,
        issueId: list[index - 1]?.id,
      });
    }
  };

  // Issue 弹框 - 下一个问题
  const nextIssue = () => {
    const index = findIndex(list, { id: issueId });

    if (index === list.length - 1) {
      if (next) {  // 当前页的最后一个问题，需列表请求后一页，取后一页的第一个 issue 展示
        getListData(pageStart + pageSize, pageSize, searchParams, (data: any) => {
          setIssueModal({
            ...issueModal,
            issueId: data[0]?.id,
          });
        });
      }
    } else {
      setIssueModal({
        ...issueModal,
        issueId: list[index + 1]?.id,
      });
    }
  };

  const onCloseIssueModal = () => {
    setIssueModal({ visible: false, issueId: null, isFirstIssue: false, isLastIssue: false });
  };

  return (
    <div className={style.ccissues}>
      <Search
        href={`${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/ccfiles`}
        searchParams={cloneDeep(searchParams)}
        loading={loading}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      <Table
        dataSource={list}
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
          title="函数名"
          dataIndex="func_name"
          render={(func_name, data: any) => (
            <>
              <a
                onClick={() => {
                  setIssueModal({
                    visible: true,
                    issueId: data.id,
                  });
                }}
                // target="_blank"
                // to={`${getProjectRouter(
                //   orgSid,
                //   teamName,
                //   repoId,
                //   projectId
                // )}/metric/ccissues/${data.id}`}
                className="link-name"
                title={data.func_name}
              >
                {data.func_name}
              </a>
            </>
          )}
        />
        <Column
          title="文件"
          dataIndex="file_path"
          width='40%'
          render={file_path => (
            <>
              <p>
                {file_path.split('/').pop()}
              </p>
              <p className={style.filePath}>{file_path}</p>
            </>
          )}
        />
        <Column
          title="圈复杂度"
          dataIndex="ccn"
          width={120}
          align='center'
        />
        <Column
          title="变更类型"
          dataIndex="change_type"
          width={120}
          render={(change_type, data: any) => (
          // todo: remove
              <span
                style={{
                  color: CC_CHANGE_TYPE_CHOICES[data.change_type].labelColor,
                }}
              >
                {CC_CHANGE_TYPE_CHOICES[data.change_type].label}
              </span>
          )}
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
      <IssueModal
        visible={issueModal.visible}
        issueId={issueModal.issueId}
        isFirstIssue={issueModal.isFirstIssue}
        isLastIssue={issueModal.isLastIssue}
        params={[orgSid, teamName, repoId, projectId]}
        prevIssue={prevIssue}
        nextIssue={nextIssue}
        onClose={onCloseIssueModal}
        callback={() => getListData()}
      />
    </div>
  );
};
export default CCIssues;
