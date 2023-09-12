// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import moment from 'moment';
import { toNumber, find } from 'lodash';

import { Button, message, Modal } from 'coding-oa-uikit';
import SelectBorderless from '@src/components/select-borderless';
import { SEVERITY, RESOLUTIONS } from '../constants';

import { useProjectMembers } from '@src/utils/hooks';
import {
  updateIssueAuthor,
  updateIssueSeverity,
  resoluteIssue,
  getIssueDetailComments,
} from '@src/services/projects';

import { getRuleDetail } from '@src/services/schemes';

import RuleDetail from './rule-detail';
import HandleModal from './handle-issue-modal';

import style from './style.scss';

interface DetailRightProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
  schemeId: number;
  issueId: number;
  curLine: number;
  data: any;
  callback: (data: any) => void;
  scrollToLine: (line: number) => void;
}

const DetailRight = (props: DetailRightProps) => {
  const [issueRecords, setIssueRecords] = useState([]);

  const [visible, setVisible] = useState(false);
  const [ruleDetail, setRuleDetail] = useState({});
  const [modalVsb, setModalVsb] = useState(false);
  const {
    orgSid,
    teamName,
    data,
    repoId,
    projectId,
    schemeId,
    issueId,
    curLine,
    callback,
    scrollToLine,
  } = props;
  const isHandled = data.state === 2;
  const members = useProjectMembers();

  useEffect(() => {
    getRecords();
  }, [issueId]);

  const getRecords = async () => {
    const issueRecords = await getIssueDetailComments(
      orgSid,
      teamName,
      repoId,
      projectId,
      issueId,
    );
    setIssueRecords(issueRecords.results || []);
  };

  const openDetail = async (id: number) => {
    setRuleDetail(await getRuleDetail(orgSid, teamName, repoId, schemeId, id));
    setVisible(true);
  };

  const operation = () => {
    if (isHandled) {
      Modal.confirm({
        title: '重新打开问题',
        content: '将问题重新标记为 未处理 状态',
        onOk: () => {
          resoluteIssue(orgSid, teamName, repoId, projectId, issueId, {
            resolution: 0,
            scope: 1,
          }).then((res) => {
            message.success('更新成功');
            callback(res);
            getRecords();
          });
        },
      });
    } else {
      setModalVsb(true);
    }
  };

  const handleIssue = (data: any) => {
    resoluteIssue(orgSid, teamName, repoId, projectId, issueId, data).then((res) => {
      message.success('更新成功');
      setModalVsb(false);
      callback(res);
      getRecords();
    });
  };

  return (
    <div className={style.right}>
      <div className={cn(style.topMsg, style.common)}>
        <div className={style.item}>
          <h3>缺陷信息</h3>
          <div className={style.msg}>
            <span className={style.label}>严重级别</span>
            <SelectBorderless
              value={data.severity}
              data={Object.keys(SEVERITY).map(item => ({
                value: toNumber(item),
                text: SEVERITY[item],
              }))}
              onChange={(value: any) => {
                updateIssueSeverity(
                  orgSid,
                  teamName,
                  repoId,
                  projectId,
                  issueId,
                  toNumber(value),
                ).then((res: any) => {
                  message.success('严重级别修改成功');
                  callback(res);
                });
              }}
            />
          </div>
          <div className={style.msg}>
            <span className={style.label}>缺陷状态</span>
            <span>{RESOLUTIONS[data.state] || data.state}</span>
          </div>
          <div className={style.msg}>
            <span className={style.label}>责任人</span>
            <SelectBorderless
              value={data.author}
              data={members.map((item: any) => ({
                value: item.username,
                text: item.nickname,
              }))}
              onChange={(value: any) => {
                updateIssueAuthor(
                  orgSid,
                  teamName,
                  repoId,
                  projectId,
                  issueId,
                  value,
                ).then((res: any) => {
                  message.success('责任人修改成功');
                  callback(res);
                });
              }}
            />
          </div>
        </div>
        <div className={style.item}>
          <h3>规则信息</h3>
          <a onClick={() => {
            openDetail(data.checkrule_gid);
          }}>
            {data.checkrule_real_name}
          </a>
        </div>
        <div className={style.item}>
          <h3>缺陷位置</h3>
          {data.issue_details?.map((item: any) => (
            <a
              key={item.issuedetail_uuid}
              onClick={() => scrollToLine(item.line)}
              className={cn({ [style.curLine]: curLine === item.line })}
            >
              第 {item.line} 行
            </a>
          ))}
          <p className={style.reason}>错误原因：{data.msg}</p>
        </div>
        <Button
          disabled={!data.id}
          style={{ marginTop: 16 }}
          onClick={() => operation()}
        >
          {isHandled ? '重新打开' : '忽略问题'}
        </Button>
      </div>
      <div className={cn(style.record, style.common)}>
        <h3>操作记录</h3>
        {issueRecords.map((item: any, index: number) => (
          <div
            key={item.id}
            className={cn(style.item, { [style.first]: index === 0 })}
          >
            <div className={style.basic}>
              <span className={style.creator}>
                {find(members, { username: item.creator })
                  ? find(members, { username: item.creator }).nickname
                  : item.creator}
              </span>
              <span className={style.time}>
                {item.created_time
                  && moment(item.created_time).format('YYYY/MM/DD HH:mm:ss')}
              </span>
            </div>
            <p className={style.message}>{item.message}</p>
          </div>
        ))}
      </div>

      <RuleDetail
        data={ruleDetail}
        visible={visible}
        onClose={() => setVisible(false)}
      />
      <HandleModal
        visible={modalVsb}
        onClose={() => setModalVsb(false)}
        onOk={handleIssue}
      />
    </div>
  );
};

export default DetailRight;
