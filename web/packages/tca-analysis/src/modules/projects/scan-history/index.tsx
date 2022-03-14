// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析历史
 */
import React, { useEffect, useState, useRef } from 'react';
import { useHistory, Link } from 'react-router-dom';
import CopyToClipboard from 'react-copy-to-clipboard';
import qs from 'qs';
import { toNumber, get } from 'lodash';

import { Table, Tooltip, message, Button } from 'coding-oa-uikit';
import Copy from 'coding-oa-uikit/lib/icon/Copy';
import RunningIcon from '@src/components/running-icon';
import Tips from '@src/components/tips';

import { getScans, cancelScan } from '@src/services/projects';
import { DEFAULT_PAGER } from '@src/common/constants';
import { formatDate, secondToDate, getQuery } from '@src/utils';
import { getProjectRouter } from '@src/utils/getRoutePath';

import successSvg from '@src/images/success.svg';
import failureSvg from '@src/images/failure.svg';
import abortedSvg from '@src/images/aborted.svg';

import { SCAN_TYPE_CHOICES } from '../constants';

import Result from './result';

import style from './style.scss';

const { Column } = Table;
let timer: any = null;

interface ScanHistoryProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
  curTab: string;
}

const ScanHistory = (props: ScanHistoryProps) => {
  const query = getQuery();
  const history = useHistory();
  const savedCallback = useRef<Function>(() => { });
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [list, setList] = useState([]);
  const [visible, setVisible] = useState(false);
  const [resData, setResData] = useState({});

  const { orgSid, teamName, repoId, projectId, curTab } = props;
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const refresh = get(history, 'location.state.refresh');

  useEffect(() => {
    savedCallback.current = getListData;
  });

  useEffect(() => {
    if (curTab === 'scan-history') {
      timer = setInterval(() => {
        savedCallback.current();
      }, 6000);
    } else {
      clearInterval(timer);
    }
    return () => clearInterval(timer);
  }, [curTab]);

  useEffect(() => {
    getListData();
  }, [projectId]);

  useEffect(() => {
    refresh && getListData();
  }, [refresh]);

  const getListData = (limit = pageSize, offset = pageStart) => {
    const params = {
      limit,
      offset,
    };
    getScans(orgSid, teamName, repoId, projectId, params).then((response) => {
      history.push(`${location.pathname}?${qs.stringify(params)}`);
      setList(response.results);
      setCount(response.count);
    });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData(pageSize, (page - 1) * pageSize);
  };

  const getStatusIcon = (status: number) => {
    if (status >= 0 && status <= 99) {
      return successSvg;
    }
    if (status >= 100 && status <= 299) {
      return failureSvg;
    }
    if (status >= 300 && status <= 399) {
      return abortedSvg;
    }

    return '';
  };

  const cancel = async (jobId: number) => {
    await cancelScan(orgSid, teamName, repoId, projectId, jobId);
    getListData();
    message.success('取消成功');
  };

  return (
    <>
      <Table
        dataSource={list}
        rowKey={(item: any) => item.id}
        className={style.scans}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: false,
          showTotal: (total, range) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
          onChange: onChangePageSize,
        }}
      >
        <Column title="分析ID" dataIndex="id" />
        <Column
          title="启动时间"
          dataIndex="create_time"
          render={(time: any) => time && formatDate(time, 'YYYY-MM-DD HH:mm')}
        />
        <Column
          title="版本"
          dataIndex="current_revision"
          render={(version: string) => version && (
            <span className={style.copyIcon}>
              {version.substring(0, 8)}
              <Tooltip title={version}>
                <CopyToClipboard
                  text={version}
                  onCopy={() => message.success('复制成功')}
                >
                  <Copy />
                </CopyToClipboard>
              </Tooltip>
            </span>
          )
          }
        />
        <Column
          title="总耗时"
          dataIndex="total_time"
          render={(time: string) => (time ? secondToDate(toNumber(time)) : '--')}
        />
        <Column
          title="状态"
          dataIndex="result_code"
          render={(status, data: any) => (status === null ? (
            <>
              <RunningIcon />
              <span className={style.running}>执行中</span>
            </>
          ) : (
            <div className={style.status}>
              <img src={getStatusIcon(status)} />
              <span>{data.result_code_msg}</span>
              {data.result_msg && <Tips title={data.result_msg} />}
            </div>
          ))
          }
        />
        <Column
          title="类型"
          dataIndex="type"
          render={type => SCAN_TYPE_CHOICES[type] || type}
        />
        <Column title="启动人" dataIndex="creator" />
        <Column
          title="操作"
          dataIndex="id"
          render={(id, data: any) => (
            <>
              <Button
                type="link"
                onClick={() => {
                  setVisible(true);
                  setResData(data as any);
                }}
              >
                分析结果
              </Button>
              <Link
                style={{ marginLeft: 10 }}
                to={`${getProjectRouter(orgSid, teamName, repoId, projectId)}/scan-history/${data.job_gid}`}
              >详情</Link>
              {data.result_code === null && (
                <Button
                  style={{ marginLeft: 10 }}
                  type="link"
                  onClick={() => cancel(data.job_gid)}
                >
                  取消
                </Button>
              )}
            </>
          )}
        />
      </Table>
      <Result data={resData} visible={visible} onClose={() => setVisible(false)} />
    </>
  );
};
export default ScanHistory;
