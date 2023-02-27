// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { toNumber } from 'lodash';
import { Button, Switch, Popover, Radio, Input, message, Tooltip } from 'coding-oa-uikit';
import Pencil from 'coding-oa-uikit/lib/icon/Pencil';

import PositionIcon from '@src/images/position.svg';
import Tips from '@src/components/tips';
import { RESOLUTIONS, SEVERITY } from '../constants';
import { updateIssueAuthor, updateIssueSeverity, resoluteIssue } from '@src/services/projects';

import style from './style.scss';

interface OperationProps {
  params: any;
  detail: any;  // issue 详情
  status: any;  // 气泡框状态
  issueLines: any;
  scrollToItem: (line: number) => void;
  reloadList: () => void;
  setPopStatus: (key?: string) => void; // 设置气泡框状态
  callback: (data: any) => void;
}

export const Operation = ({
  params,
  detail,
  status,
  issueLines,
  scrollToItem,
  reloadList,
  setPopStatus,
  callback,
}: OperationProps) => {
  const [severity, setSeverity] = useState(detail.severity);
  const [author, setAuthor] = useState('');
  const [ignoreType, setType] = useState();
  const [scope, setScope] = useState(1);
  const { severityPopVsb, authorPopVsb, issuePopVsb, issueLinePopVsb } = status;
  const [orgSid, teamName, repoId, projectId] = params;
  const isHandled = detail.state === 2;

  const onPopReset = () => {
    setPopStatus();
    setSeverity(detail.severity);
    setAuthor('');
    setScope(1);
    setType(undefined);
  };

  const updateSeverity = () => {
    updateIssueSeverity(...params, detail.id, severity).then(() => {
      message.success('严重级别修改成功');
      successCallback({ severity });
    });
  };

  const updateAuthor = () => {
    updateIssueAuthor(orgSid, teamName, repoId, projectId, detail.id, author).then(() => {
      message.success('责任人修改成功');
      successCallback({ author });
    });
  };

  const handleIssue = () => {
    const data = {
      resolution: isHandled ? 0 : ignoreType,
      scope: isHandled ? 1 : scope,
    };
    resoluteIssue(orgSid, teamName, repoId, projectId, detail.id, data).then((res) => {
      message.success(isHandled ? '已重新打开问题' : '已忽略问题');
      successCallback({ state: res.state });
    });
  };

  const successCallback = (data: any) => {
    setPopStatus();
    reloadList();
    callback(data);
  };

  return (
    <div className={style.operationWrapper}>
      <div>
        <span className={style[`status-${detail.state}`]}>{RESOLUTIONS[detail.state] || detail.state}</span>
        <span className="ml-12">
          <span className="text-grey-7">严重级别：</span>
          {SEVERITY[detail.severity]}
          <IssuePopover
            title='修改严重级别'
            visible={severityPopVsb}
            onCancel={onPopReset}
            onOk={updateSeverity}
            content={
              <Radio.Group value={severity} onChange={e => setSeverity(e.target.value)}>
                {Object.keys(SEVERITY).map(item => (
                  <Radio key={item} value={toNumber(item)}>{SEVERITY[item]}</Radio>
                ))}
              </Radio.Group>
            }
          >
            <Tips
              icon={
                <Pencil className={style.editIcon} onClick={() => {
                  setPopStatus('severityPopVsb');
                }} />
              }
              title='修改严重级别'
            />
          </IssuePopover>
        </span>
        <span className="ml-12">
          <span className="text-grey-7">责任人：</span>
          {detail.author}
          <IssuePopover
            title='修改责任人'
            visible={authorPopVsb}
            onCancel={onPopReset}
            onOk={updateAuthor}
            content={
              <Input
                placeholder='请输入责任人'
                size='middle'
                value={author}
                onChange={e => setAuthor(e.target.value)}
              />
            }
          >
            <Tips
              icon={
                <Pencil className={style.editIcon} onClick={() => {
                  setPopStatus('authorPopVsb');
                }} />
              }
              title='修改责任人'
            />
          </IssuePopover>
        </span>
      </div>
      <div>
        {
          issueLines.length === 1 && (
            <Tooltip title='定位问题'>
              <Button
                shape="circle"
                icon={<img src={PositionIcon} />}
                onClick={() => {
                  scrollToItem(issueLines[0]);
                }}
              />
            </Tooltip>
          )
        }
        {
          issueLines.length > 1 && (
            <IssuePopover
              title='问题所在行'
              visible={issueLinePopVsb}
              onCancel={onPopReset}
              onCancelText="关闭"
              content={
                <div>
                  {
                    issueLines.map((line: number) => (
                      <a
                        key={line}
                        style={{ display: 'inline-block', minWidth: '88px' }}
                        onClick={() => {
                          scrollToItem(line);
                        }}>第 {line} 行</a>
                    ))
                  }
                </div>
              }
            >
              <Tooltip title='定位问题'>
                <Button
                  shape="circle"
                  icon={<img src={PositionIcon} />}
                  onClick={() => {
                    setPopStatus('issueLinePopVsb');
                  }}
                />
              </Tooltip>
            </IssuePopover>
          )
        }
        <IssuePopover
          title={isHandled ? '重新打开问题' : '标记处理'}
          visible={issuePopVsb}
          onCancel={onPopReset}
          onOk={handleIssue}
          content={
            isHandled ? (
              <p className={style.nowrap}>将问题重新标记为【未处理】状态</p>
            ) : (
              <>
                <p className={style.nowrap}>请选择处理问题方式，提交后问题状态将置为已处理</p>
                <Radio.Group
                  value={ignoreType}
                  onChange={(e) => {
                    if (e.target.value === 1) {
                      setScope(1);
                    }
                    setType(e.target.value);
                  }}
                >
                  <Radio value={1}>已修复</Radio>
                  <Radio value={2}>无需修复</Radio>
                  <Radio value={3}>误报</Radio>
                </Radio.Group>
                {
                  (ignoreType === 2 || ignoreType === 3) && (
                    <p style={{ marginTop: 10 }}>
                      <Switch
                        checked={scope === 2}
                        onChange={(checked) => {
                          setScope(checked ? 2 : 1);
                        }}
                      />&nbsp;全局忽略
                      <Tips title='开启全局忽略后，代码库内其他分析项目扫出相同问题会直接复用当前忽略方式，请谨慎操作！' />
                    </p>
                  )
                }

              </>
            )
          }
        >
          <Button
            className="ml-12"
            onClick={() => setPopStatus('issuePopVsb')}
          >{isHandled ? '重新打开' : '标记处理'}</Button>
        </IssuePopover>
      </div>
    </div>
  );
};

/**
 * 简单封装 Popover 组件
 */
const IssuePopover = ({ title, visible, children, content, onOk, onCancel, onCancelText, showFooter = true }: any) => (
  <Popover
    title={title}
    visible={visible}
    placement='bottom'
    mouseEnterDelay={0}
    overlayClassName={style.statusPopover}
    content={
      <div>
        {content}
        {
          showFooter && (
            <div className={style.footer}>
              {
                onOk && <Button size='small' type='primary' onClick={onOk}>确认</Button>
              }
              {
                onCancel && <Button size='small' onClick={onCancel}>{onCancelText || '取消'}</Button>
              }
            </div>
          )
        }
      </div>
    }
  >
    {children}
  </Popover>
);
