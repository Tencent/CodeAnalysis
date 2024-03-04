// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 工具分析详情
 */
import React, { useState, useEffect } from 'react';
// import { Link, useParams } from 'react-router-dom';
import { useParams } from 'react-router-dom';
import cn from 'classnames';
import moment from 'moment';
import { get, isNumber } from 'lodash';

import { Button, Table, Avatar } from 'coding-oa-uikit';
import RunningIcon from '@src/components/running-icon';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

// import { getProjectRouter } from '@src/utils/getRoutePath';
import { DEFAULT_PAGER } from '@src/constant';
import {
  getCodeToolDetail,
  getCodeToolScans,
  getCodeToolParams,
} from '@src/services/projects';

import { TOOLS_STATUS } from '../constants';

import ScanModal from './modal';

import style from './style.scss';

const { Column } = Table;

interface ScansProps {
  repoId: number;
  projectId: number;
}

const Scans = (props: ScansProps) => {
  const [toolDetail, setToolDetail] = useState({}) as any;
  // const [toolDetail, setToolDetail] = useState(mockDetail) as any;
  const [list, setList] = useState([]) as any;
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const [visible, setVisible] = useState(false);
  const [scanParams, setScanParams] = useState([]) as any;
  const { toolName = '' } = useParams() as any;
  const { repoId, projectId } = props;
  const { count, pageSize, pageStart } = pager;

  useEffect(() => {
    (async () => {
      const params = await getCodeToolParams(repoId, projectId, toolName);
      const detail = await getCodeToolDetail(repoId, projectId, toolName);
      setToolDetail(detail || {});
      setScanParams(params.results || []);
    })();

    getScansList();
  }, [toolName]);

  const onChangePageSize = (page: number, pageSize: number) => {
    getScansList((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getScansList(DEFAULT_PAGER.pageStart, size);
  };

  const getScansList = async (
    offset = DEFAULT_PAGER.pageStart,
    limit = DEFAULT_PAGER.pageSize,
  ) => {
    const res =      (await getCodeToolScans(projectId, toolName, { offset, limit })) || {};

    setPager({
      pageSize: limit,
      pageStart: offset,
      count: res.count,
    });
    setList(res.results || []);
    // setList(mockList.results);
  };

  const getToolStatus = (code: any) => {
    if (code >= 0 && code <= 99) {
      return 'success';
    }
    if (code >= 100 && code <= 299) {
      return 'failed';
    }
    if (code >= 300 && code <= 399) {
      return 'aborted';
    }
    return '';
  };

  const {
    display_name: displayName,
    status,
    description,
  } = toolDetail.checktool || {};

  return (
    <div className={cn(style.toolCommon, style.toolDetail)}>
      <div className={style.header}>
        <div>
          <span className={style.title}>{displayName}</span>
          <span className={cn(style.toolStatus, style[`status${status}`])}>
            {TOOLS_STATUS[status]}
          </span>
        </div>
        <Button type="primary" onClick={() => setVisible(true)}>
          启动任务
        </Button>
      </div>
      <p className={style.subTitle}>工具介绍</p>
      <p className={style.toolDesc}>{description}</p>
      {/* {
          toolName === 'codehotspot' && (
              <p className={style.tips}>
                  Tips: 下载结果数据后，请点击
                  <Link
                  target='_blank' to={`${getProjectRouter(repoId, projectId)}/code-tools/${toolName}/circle-packing`}
                  >数据解析器</Link>
                      查看结果
              </p>
          )
      } */}

      <Table
        size="small"
        dataSource={list}
        // scroll={{x: 1500}}
        rowKey={(item: any, index) => `${item.id}${index}`}
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
        <Column title="Job ID" dataIndex={['scan', 'job_gid']} />
        <Column
          title="启动时间"
          dataIndex={['scan', 'scan_time']}
          render={time => time
            && moment(time, 'YYYY-MM-DD HH:mm:ss').format('YYYY-MM-DD HH:mm:ss')
          }
        />
        <Column
          title="耗时"
          dataIndex={['scan', 'total_time']}
          // render={time => time && formatTime(parseInt(time))}
        />
        <Column
          title="状态"
          dataIndex={['scan', 'result_code']}
          render={(code, item) => (code === null ? (
              <RunningIcon />
          ) : (
              <div
                className={cn(style.status, {
                  [style[getToolStatus(code)]]: isNumber(code),
                })}
              >
                {get(item, 'scan.result_code_msg')}
              </div>
          ))
          }
        />
        <Column
          title="启动人"
          dataIndex={['scan', 'creator']}
          render={creator => creator && (
              <>
                <Avatar size={24} icon={<UserIcon />} />
                &nbsp;{creator}
              </>
          )
          }
        />
        <Column
          title="操作"
          dataIndex="id"
          width={280}
          render={(id, item: any) => (
            <>
              {item.result_data_url && (
                <a href={item.result_data_url}>下载结果文件</a>
              )}
              {item.result_other_url && (
                <a href={item.result_other_url} style={{ marginLeft: 12 }}>
                  下载其他文件
                </a>
              )}
            </>
          )}
        />
      </Table>
      <ScanModal
        visible={visible}
        params={{ repoId, projectId, toolName }}
        onHide={() => setVisible(false)}
        scanParams={scanParams}
        callback={() => {
          getScansList();
        }}
      />
    </div>
  );
};

export default Scans;
