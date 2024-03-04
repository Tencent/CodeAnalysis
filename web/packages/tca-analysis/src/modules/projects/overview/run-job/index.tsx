// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import cn from 'classnames';
import Scan from 'coding-oa-uikit/lib/icon/Scan';
// 项目内
import { formatDateTime } from '@src/utils';
import Copy from '@src/components/copy';
import style from './style.scss';
import { Tooltip } from 'coding-oa-uikit';

const STATUS_TYPE = {
  SUCCESS: 'success',
  ERROR: 'error',
  RUNNING: 'running',
};

const STATUS = {
  [STATUS_TYPE.SUCCESS]: '成功',
  [STATUS_TYPE.ERROR]: '失败',
  [STATUS_TYPE.RUNNING]: '进行中',
};

interface IProps {
  latestScan: any;
  count: number;
}
const RunJob = ({ latestScan, count }: IProps) => {
  const code = latestScan.result_code;

  const getStatus = (code: number | null) => {
    let type = STATUS_TYPE.SUCCESS;
    if (code === null) {
      type = STATUS_TYPE.RUNNING;
    } else if (code >= 100) {
      type = STATUS_TYPE.ERROR;
    }
    return {
      status: STATUS[type],
      type,
    };
  };

  const renderResult = () => (
        <span className={cn(style.bold, style[getStatus(code).type])}>
            {getStatus(code).status}
            {
                getStatus(code).type === STATUS_TYPE.RUNNING && (
                    <Scan className={style.running} />
                )
            }
        </span>
  );

  return (
        <div className={style.latestScan}>
            <span>
                累计分析<span className={cn(style.bold, style.default)}>{count}</span>次，
                最近一次分析
                {
                    getStatus(code).type === STATUS_TYPE.ERROR ? (
                        <Tooltip title={latestScan.result_code_msg}>
                            {renderResult()}
                        </Tooltip>
                    ) : renderResult()

                }
            </span>
            {
                latestScan.current_revision && (
                    <span className={style.desc}>
                        版本：{latestScan.current_revision.substr(0, 8)}
                        <Copy
                            text={latestScan.current_revision}
                            copyText={latestScan.current_revision.substr(0, 8)}
                        />
                    </span>
                )
            }
            <span className={style.desc}>启动人：{latestScan.creator}</span>
            <span className={style.desc}>启动时间：{formatDateTime(latestScan.scan_time)}</span>
        </div>
  );
};
export default RunJob;
