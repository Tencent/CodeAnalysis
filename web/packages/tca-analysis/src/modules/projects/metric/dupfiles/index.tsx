// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果 - 重复代码 - 列表页
 */
import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import { cloneDeep, toNumber, omit, omitBy, isString } from 'lodash';
import qs from 'qs';
import { Table, Avatar } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

import { getQuery } from '@src/utils';
import { getDupIssues } from '@src/services/projects';
import { DEFAULT_PAGER } from '@src/constant';
import { getProjectBlankRouter } from '@src/utils/getRoutePath';
import { DUP_FILE_STATE_OPTIONS } from '../../constants';

import Search from './search';
import style from './style.scss';

const { Column } = Table;

interface SortType {
  key: string;
  order: 'ascend' | 'descend' | undefined;
}

interface DupFilesProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
}

const DupFiles = (props: DupFilesProps) => {
  const history = useHistory();

  const { orgSid, teamName, repoId, projectId } = props;
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [dupIssues, setDupIssues] = useState([]);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const ordering: string = isString(query.ordering) ? query.ordering : '';
  const sort: SortType = {
    key: ordering.replace('-', ''),
    order: ordering.includes('-') ? 'descend' : 'ascend',
  };
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
    getDupIssues(orgSid, teamName, repoId, projectId, params)
      .then((response: any) => {
        setCount(response.count);
        history.push(`${location.pathname}?${qs.stringify(params)}`);
        setDupIssues(response.results || []);
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

  /**
     * 列表排序
     * @param pagination 分页参数
     * @param filters 过滤参数
     * @param sorter 排序参数
     * @param extra 其他
     */
  const onFilterChange = (pagination: any, filters: any, sorter: any, extra: any) => {
    if (extra.action === 'sort') {
      getListData(DEFAULT_PAGER.pageStart, pageSize, {
        ...searchParams,
        ordering: sorter.order
          ? `${sorter.order === 'descend' ? '-' : ''}${sorter.columnKey}`
          : '',
      });
    }
  };

  return (
    <div>
      <Search
        searchParams={cloneDeep(searchParams)}
        loading={loading}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      <Table
        dataSource={dupIssues}
        rowKey={(item: any) => item.id}
        onChange={onFilterChange}
        pagination={{
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
          dataIndex="file_name"
          key="file_name"
          sorter
          sortOrder={sort.key === 'file_name' ? sort.order : undefined}
          render={(file_name, data: any) => (
            <a
              target="_blank"
              href={`${getProjectBlankRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
              )}/metric/dupfiles/${data.id}`}
              className="link-name"
              title={data.file_path} rel="noreferrer"
            >
              <p>{file_name}</p>
              <p className="path">{data.file_path}</p>
            </a>
          )}
        />
        <Column
          title="重复行数"
          dataIndex="total_duplicate_line_count"
          key="total_duplicate_line_count"
          sorter
          sortOrder={sort.key === 'total_duplicate_line_count' ? sort.order : undefined}
          render={total_duplicate_line_count => total_duplicate_line_count && (
            <div>{total_duplicate_line_count}</div>
          )
          }
        />
        <Column
          title="总行数"
          dataIndex="total_line_count"
          key="total_line_count"
          sorter
          sortOrder={sort.key === 'total_line_count' ? sort.order : undefined}
          render={total_line_count => total_line_count && <div>{total_line_count}</div>
          }
        />
        <Column
          title="重复块数"
          dataIndex="block_num"
          key="block_num"
          sorter
          sortOrder={sort.key === 'block_num' ? sort.order : undefined}
          render={block_num => block_num && <div>{block_num}</div>}
        />
        <Column
          title="重复率"
          dataIndex="duplicate_rate"
          key="duplicate_rate"
          sorter
          sortOrder={sort.key === 'duplicate_rate' ? sort.order : undefined}
          render={(duplicate_rate, data: any) => (
            // const progress = [
            //   {
            //     value: data.duplicate_rate,
            //     text: 'completed',
            //     name: '已完成',
            //     color: 'completed',
            //   },
            //   {
            //     value: 100 - data.duplicate_rate,
            //     text: 'uncompleted',
            //     name: '未完成',
            //     color: 'uncompleted',
            //   },
            // ];
            <div className={style.progressWrapper}>
              {/* todo: remove */}
              {/* <ProgressBar
                                    className={style.progressSize}
                                    progress={progress}
                                    parentRef={null}
                                    percent={data.duplicate_rate}
                                /> */}
              <span className={style.percentage}>
                {' '}
                {data.duplicate_rate}%
              </span>
            </div>
          )
          }
        />
        <Column
          title="状态"
          dataIndex="state"
          key="issue_state"
          sorter
          sortOrder={sort.key === 'issue_state' ? sort.order : undefined}
          render={(issue, data: any) => data && (
            <div
              className={style.fileState}
              style={{
                background: `${DUP_FILE_STATE_OPTIONS[data.issue.state - 1].color
                }`,
              }}
            >
              {DUP_FILE_STATE_OPTIONS[data.issue.state - 1].text}
            </div>
          )
          }
        />
        <Column
          title="责任人"
          dataIndex="owner"
          key="issue_owner"
          sorter
          sortOrder={sort.key === 'issue_owner' ? sort.order : undefined}
          render={(issue, data: any) => (data ? (
            <>
              <Avatar size={24} icon={<UserIcon />} /> {data.issue.owner}
            </>
          ) : (
            '未分配'
          ))
          }
        />
      </Table>
    </div>
  );
};
export default DupFiles;
