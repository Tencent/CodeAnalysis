/**
 * 扫描详情
 */

import React, { useEffect, useState, useRef } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { useSelector } from 'react-redux';
import cn from 'classnames';
import qs from 'qs';
import { find, isEmpty, toNumber, get } from 'lodash';

import { Steps, Tooltip, Tabs, Tag, Button, message } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';
import Waiting from 'coding-oa-uikit/lib/icon/Waiting';
import Success from 'coding-oa-uikit/lib/icon/Success';
import Failed from 'coding-oa-uikit/lib/icon/Failed';
import Runing from 'coding-oa-uikit/lib/icon/Runing';
import AttentionRed from 'coding-oa-uikit/lib/icon/AttentionRed';
import Attention from 'coding-oa-uikit/lib/icon/Attention';
import CloudDownload from 'coding-oa-uikit/lib/icon/CloudDownload';

import { getProjectRouter, getSchemeBlankRouter } from '@src/utils/getRoutePath';
import { getScanDetail, getTaskDetail, getLog, cancelScan } from '@src/services/projects';
import { getQuery, formatDateTime } from '@src/utils';

import Result from './result';
import style from './style.scss';

const { Step } = Steps;

enum StatusCode {
  WAITING, // 0 - 等待
  RUNNING, // 1 - 执行中
  FINISHED, // 2 - 已完成
  CLOSING, // 3 - 入库中
}

const STATUS_TYPE = {
  WAIT: 'wait',
  PROCESS: 'process',
  FINISH: 'finish',
  ERROR: 'error',
};

const PROCESS = {
  compile: '编译',
  analyze: '分析',
  datahandle: '数据处理',
};

const ScanDetail = () => {
  const intervalRef = useRef();
  const history = useHistory();
  const { orgSid, teamName, repoId, projectId, jobId, scanTab } = useParams() as any;
  const [data, setData] = useState<any>({});
  const [curTask, setCurTask] = useState<any>({});
  const taskRef = useRef() as any; // 存储当前任务的id，解决定时器中的闭包问题 - 获取不到最新的 curTask 值
  const APP = useSelector((state: any) => state.APP);
  const isSuperuser = get(APP, 'user.is_superuser', false);

  useEffect(() => {
    const query = getQuery();

    if (query.taskId) {
      taskRef.current = toNumber(query.taskId);
    }
    getJobDetail();

    return () => {
      intervalRef.current && clearInterval(intervalRef.current);
    };
  }, [jobId]);

  const getJobDetail = () => {
    getScanDetail(orgSid, teamName, repoId, projectId, jobId).then((res) => {
      setData(res);
      let task = find(res.task_set, { id: taskRef.current });

      if (!task) {
        task = res.task_set.length > 0 ? res.task_set[0] : {};
      }

      task.id && getTaskDetailData(task.id);

      if (res.state === StatusCode.FINISHED && intervalRef.current) {
        clearInterval(intervalRef.current);
      } else if (res.state !== StatusCode.FINISHED && !intervalRef.current) {
        intervalRef.current = setInterval(() => {
          getJobDetail();
        }, 5000) as any;
      }
    });
  };

  const getTaskDetailData = async (taskId: number) => {
    const res = await getTaskDetail(orgSid, teamName, repoId, projectId, jobId, taskId);
    setCurTask(res);
    history.push(`${location.pathname}?${qs.stringify({
      taskId,
    })}`);
  };

  const downloadLog = (url: string) => {
    // 跨域兼容处理，将log内的url的origin进行替换
    const a = document.createElement('a');
    a.href = decodeURIComponent(url) || '';
    // 替换为前端域名地址
    let { pathname } = a;
    if (!pathname.startsWith('/server')) {
      pathname = `/server${pathname}`;
    }
    url = `${window.location.origin}${pathname}`;
    const filename = url.substr(url.lastIndexOf('/') + 1);
    getLog(url).then(res => res.blob().then((blob) => {
      const blobUrl = window.URL.createObjectURL(blob);
      const a: any = document.getElementById('downloadLog');
      a.href = blobUrl;
      a.download = filename;
      a.click();
      window.URL.revokeObjectURL(blobUrl);
    }));
  };

  const getStatusDesc = (item: any) => {
    const status = item.state;
    switch (status) {
      case StatusCode.WAITING:
        return <p className={style.desc}>等待执行：{item.waiting_time.split('.')[0]}</p>;
      case StatusCode.RUNNING:
        return <p className={style.desc}>正在执行：{item.execute_time?.split('.')[0]}</p>;
      case StatusCode.FINISHED:
        return (
          <>
            <p className={style.desc}>执行结束：{item.result_code_msg}</p>
            <p className={style.desc}>执行耗时：{item.execute_time?.split('.')[0]}</p>
          </>
        );
      default:
        return null;
    }
  };

  /**
     * 任务详情图标
     */
  const getTaskIcon = (state: number, code: number) => {
    if (state === StatusCode.RUNNING) {
      return getProgressIcon(STATUS_TYPE.PROCESS);
    } if (state === StatusCode.FINISHED && code >= 100) {
      // 特殊处理 299 错误，299 - 其他任务失败取消
      return code === 299 ? <Attention /> : getProgressIcon(STATUS_TYPE.ERROR);
    } if (state === StatusCode.FINISHED && code >= 0 && code < 100) {
      // 成功
      return getProgressIcon(STATUS_TYPE.FINISH);
    }
    return getProgressIcon(STATUS_TYPE.WAIT);
  };

  const getProgressIcon = (state: string) => {
    switch (state) {
      case STATUS_TYPE.WAIT: // 等待状态
        return <Waiting />;
      case STATUS_TYPE.PROCESS: // 执行中状态
        return <Runing className={style.running} />;
      case STATUS_TYPE.ERROR: // 错误状态
        return <Failed />;
      case 'attention': // 上一个步骤错误，下一步骤的状态
        return <AttentionRed />;
      case STATUS_TYPE.FINISH: // 成功状态
        return <Success />;
      default:
        return null; // 未开始，默认显示步骤数字
    }
  };

  const getProgressState = (step: number) => {
    const { state, result_code: resultCode, task_set: taskSet } = data;
    let status: string | null = STATUS_TYPE.WAIT;

    switch (step) {
      case 1: {
        if (state >= StatusCode.WAITING) {
          status = STATUS_TYPE.FINISH;
        }
        break;
      }
      case 2: {
        if (state === StatusCode.RUNNING) {
          status = STATUS_TYPE.PROCESS;
        } else if (state === StatusCode.FINISHED || state === StatusCode.CLOSING) {
          status = taskSet.some((item: any) => item.result_code >= 100)
            ? STATUS_TYPE.ERROR
            : STATUS_TYPE.FINISH;
        }
        break;
      }
      case 3: {
        if (state === StatusCode.FINISHED) {
          if (resultCode < 100) {
            status = STATUS_TYPE.FINISH;
          } else {
            // 所有子任务均成功，但最终状态失败，即入库阶段失败
            if (taskSet.every((item: any) => item.result_code < 100)) {
              status = STATUS_TYPE.ERROR;
            } else {
              // 上一步骤执行失败
              status = 'attention';
            }
          }
        } else if (state === StatusCode.CLOSING) {
          status = STATUS_TYPE.PROCESS;
        } else {
          status = null;
        }
        break;
      }
      case 4: {
        if (state === StatusCode.FINISHED) {
          status = resultCode < 100 ? STATUS_TYPE.FINISH : 'attention';
        } else {
          status = null;
        }
        break;
      }
    }
    return {
      icon: status ? getProgressIcon(status) : null,
      status: status === 'attention' ? 'error' : status,
    };
  };

  // 数据入库状态描述
  const getStep3Desc = (data: any) => {
    if (data.state === StatusCode.FINISHED) {
      return (
        <div>
          {data.end_time && <p>执行结束：{formatDateTime(data.end_time)}</p>}
          <p>
            执行结果：{data.result_code_msg} {data.result_msg}
          </p>
        </div>
      );
    }

    if (data.state === StatusCode.CLOSING) {
      return <p>入库中</p>;
    }
    return null;
  };

  /**
 * 取消分析
 */
  const onCancel = () => {
    cancelScan(orgSid, teamName, repoId, projectId, jobId).then(() => {
      message.success('任务已取消');
      getJobDetail();
    });
  };

  return (
    <div className={style.scanDetail}>
      <div className={style.header}>
        <div style={{ display: 'flex' }}>
          <span
            className={style.backIcon}
            onClick={() => history.push(`${getProjectRouter(
              orgSid,
              teamName,
              repoId,
              projectId,
            )}/scan-history`)
            }
          >
            <ArrowLeft />
          </span>
          <div className={style.right}>
            <h2 className={style.title}>
              任务执行情况
              <Tag style={{ marginLeft: 10 }}>Job ID: {jobId}</Tag>
              <Tag>Scan ID: {data?.scan_id}</Tag>
              <a
                className={style.detailBtn}
                target='_blank'
                href={`${getSchemeBlankRouter(
                  orgSid,
                  teamName,
                  repoId,
                  data?.project?.scan_scheme,
                )}/basic`} rel="noreferrer"
              >查看分析方案</a>
            </h2>
            <p className={style.desc}>
              代码库：{data?.project?.repo_scm_url}
              <span className='ml-sm'>分支：{data?.project?.branch}</span>
            </p>
          </div>
        </div>
        {
          data.result_code === null && (
            <Button type="primary" danger onClick={onCancel}>取消分析</Button>
          )
        }
      </div>
      <Tabs
        activeKey={scanTab || 'detail'}
        onChange={(tab: string) => history.push(`${getProjectRouter(
          orgSid,
          teamName,
          repoId,
          projectId,
        )}/scan-history/${jobId}/${tab}`)
        }
      >
        <Tabs.TabPane tab="执行详情" key="detail">
          <Steps direction="vertical">
            <Step
              title="创建任务"
              status={getProgressState(1)?.status as any}
              icon={getProgressState(1)?.icon}
              description={
                <div>
                  <p>创建时间：{formatDateTime(data.create_time)}</p>
                  <p>等待耗时：{data.waiting_time?.split('.')[0]}</p>
                </div>
              }
            />
            <Step
              title="并行执行子任务"
              status={getProgressState(2)?.status as any}
              icon={getProgressState(2)?.icon}
              description={
                <div>
                  {data.state !== StatusCode.WAITING && data.start_time && (
                    <p style={{ marginBottom: 10 }}>
                      执行开始时间：{formatDateTime(data.start_time)} &nbsp;
                      执行耗时：{data.execute_time?.split('.')[0]}
                    </p>
                  )}
                  <div className={style.taskItemWrapper}>
                    {data.task_set?.map((item: any, index: number) => (
                      <Tooltip
                        key={item.id}
                        overlayStyle={
                          item.state !== StatusCode.FINISHED
                            ? { display: 'none' }
                            : {}
                        }
                        title={
                          <>
                            {item.start_time && (
                              <p>
                                执行耗时：{item.execute_time?.split('.')[0]}
                              </p>
                            )}
                            {item.start_time && (
                              <p>
                                执行开始时间：
                                {formatDateTime(item.start_time)}
                              </p>
                            )}
                            {item.end_time && (
                              <p>
                                执行结束时间：
                                {formatDateTime(item.end_time)}
                              </p>
                            )}
                          </>
                        }
                      >
                        <div
                          className={cn(style.taskItem, {
                            [style.active]: item.id === curTask.id,
                          })}
                          onClick={() => {
                            getTaskDetailData(item.id);
                            taskRef.current = item.id;
                          }}
                        >
                          <p className={style.taskHeader}>
                            <span>
                              {item.task_name || `子任务${index + 1}`}
                            </span>
                            {getTaskIcon(item.state, item.result_code)}
                          </p>
                          {getStatusDesc(item)}
                        </div>
                      </Tooltip>
                    ))}
                  </div>
                  <div>
                    <h4>执行详情</h4>
                    <p className={style.tag}>执行标签：{curTask.tag}</p>
                    {!isEmpty(curTask.taskprocessrelation_set) && (
                      <Steps
                        progressDot
                        direction="vertical"
                        current={curTask.taskprocessrelation_set.length}
                        className={style.taskDetailProgress}
                      >
                        {curTask.taskprocessrelation_set.map((item: any) => (
                          <Step
                            key={item.id}
                            title={`进程 ${item.priority} : ${PROCESS[item.process] || item.process}`}
                            description={
                              <div className={style.progressItem}>
                                {item.state === StatusCode.WAITING
                                  && item.taskprocessnodequeue_set && (
                                    <div className={style.nodes}>
                                      <p>等待执行</p>
                                      <p>分配队列：</p>
                                      <ul>
                                        {item.taskprocessnodequeue_set.map((queueProcess: any, index: number) => (
                                          <li key={index}>
                                            {
                                              queueProcess
                                                .node
                                                ?.name
                                            }
                                            （
                                            {
                                              queueProcess
                                                .node
                                                ?.get_enabled_display
                                            }{' '}
                                            --{' '}
                                            {
                                              queueProcess
                                                .node
                                                ?.get_state_display
                                            }
                                            ）
                                          </li>
                                        ))}
                                      </ul>
                                    </div>
                                )}
                                {item.node?.name && (
                                  <p>执行机器: {item.node.name}</p>
                                )}
                                {item.result_code !== null && (
                                  <p>
                                    执行结束: {item.result_code_msg}{' '}
                                    {item.result_msg}
                                  </p>
                                )}
                                {item.log_url && (
                                  <p>
                                    更多详情:&nbsp;
                                    <a
                                      onClick={() => {
                                        downloadLog(item.log_url);
                                      }}
                                    >
                                      进程日志
                                    </a>
                                  </p>
                                )}
                              </div>
                            }
                          />
                        ))}
                      </Steps>
                    )}
                    <h4>任务输出</h4>
                    <div className={style.taskLog}>
                      <p>
                        <span className={style.time}>
                          {formatDateTime(curTask.create_time)}
                        </span>
                        等待耗时：{curTask.waiting_time?.split('.')[0]}{' '}
                        创建任务，等待执行
                      </p>
                      {curTask.start_time && (
                        <p>
                          <span className={style.time}>
                            {formatDateTime(curTask.start_time)}
                          </span>
                          执行耗时：{curTask.execute_time?.split('.')[0]}{' '}
                          开始执行子任务
                        </p>
                      )}
                      {curTask.taskprogress_set?.map((item: any, index: number) => (
                        <p key={item.id}>
                          <span className={style.time}>
                            {formatDateTime(item.create_time)}
                          </span>
                          步骤 {index + 1} &nbsp;
                          {item.node?.name && (
                            <span>[节点：{item.node.name}]</span>
                          )}
                          ：{item.progress_rate}%&nbsp;&nbsp;----&nbsp;&nbsp;
                          {item.message}
                        </p>
                      ))}
                    </div>
                    <h4>任务信息</h4>
                    <p>
                      <span style={{ marginRight: 10 }}>
                        创建版本：{curTask.create_version}
                      </span>
                      {curTask.execute_version && (
                        <span style={{ marginRight: 10 }}>
                          执行版本：{curTask.execute_version}
                        </span>
                      )}
                      {curTask.params_path && isSuperuser && (
                        <a style={{ marginRight: 10 }} onClick={() => {
                          downloadLog(curTask.params_path);
                        }} className={style.detailBtn}> <CloudDownload /> 下载任务参数</a>
                      )}
                      {curTask.result_path && (
                        <a style={{ marginRight: 10 }} onClick={() => {
                          downloadLog(curTask.result_path);
                        }} className={style.detailBtn}> <CloudDownload /> 下载任务结果</a>
                      )}
                      {curTask.log_url && (
                        <a onClick={() => {
                          downloadLog(curTask.log_url);
                        }} className={style.detailBtn}> <CloudDownload /> 下载执行日志</a>
                      )}
                    </p>
                  </div>
                </div>
              }
            />

            <Step
              title="数据入库"
              status={getProgressState(3)?.status as any}
              icon={getProgressState(3)?.icon}
              description={getStep3Desc(data)}
            />
            <Step
              title="完成"
              status={getProgressState(4)?.status as any}
              icon={getProgressState(4)?.icon}
            />
          </Steps>
          <a id="downloadLog" />
        </Tabs.TabPane>
        <Tabs.TabPane tab="执行结果" key="result">
          <Result scanId={data.scan_id} />
        </Tabs.TabPane>
      </Tabs>
    </div>
  );
};

export default ScanDetail;
