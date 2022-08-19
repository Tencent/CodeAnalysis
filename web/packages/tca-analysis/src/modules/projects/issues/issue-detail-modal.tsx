// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * issue 弹框
 */

import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import cn from 'classnames';
import AutoSizer from 'react-virtualized-auto-sizer';
import Highlight from 'react-highlight';
import { VariableSizeList as List } from 'react-window';
import { isEmpty, get } from 'lodash';
import { Modal, Button, Tooltip } from 'coding-oa-uikit';
import InfoCircle from 'coding-oa-uikit/lib/icon/InfoCircle';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';

import Loading from '@src/components/loading';
import { getIssueDetail, getCodeFile } from '@src/services/projects';
import { getRuleDetail } from '@src/services/schemes';

import { Operation } from './issue-popover';
import style from './style.scss';

interface IssueModalProps {
  curSchemeId: number;
  params: any;
  visible: boolean;
  issueId: number | null;
  isFirstIssue: boolean;
  isLastIssue: boolean;
  prevIssue: () => void;
  nextIssue: () => void;
  onClose: () => void;
  callback: () => void;
}

const IssueModal = (props: IssueModalProps) => {
  const {
    params, curSchemeId, issueId, visible, isFirstIssue, isLastIssue,
    prevIssue, nextIssue, onClose, callback,
  } = props;
  const [orgSid, teamName, repoId, projectId] = params;
  const listRef: any = useRef({});
  const rowHeights = useRef({});
  const [reloadList, setReloadList] = useState(false);  // 弹框关闭后是否需要重新请求列表数据
  const [detail, setDetail] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [codeFile, setCode] = useState<any>({});
  const [status, setStatus] = useState({
    severityPopVsb: false,
    authorPopVsb: false,
    issuePopVsb: false,
    rulePopVsb: false,
    issueLinePopVsb: false,
  });
  const [ruleDetail, setRuleDetail] = useState({});

  const issueLines = detail.issue_details?.map((item: any) => item.line) ?? [];

  useEffect(() => {
    if (visible && issueId) {
      getIssueDetail(orgSid, teamName, repoId, projectId, issueId).then((res) => {
        const params: any = {
          path: res.file_path,
          revision: get(res, 'issue_details[0].scan_revision'),
        };
        if (res.is_external) { // 外部代码库需要传url
          params.scm_url = res.scm_url;
          params.path = res.real_file_path;
        }
        setDetail(res);
        setLoading(true);
        getCodeFile(orgSid, teamName, repoId, projectId, params).then((file) => {
          setCode(file);
        })
          .finally(() => {
            setLoading(false);
            scrollToItem(res?.issue_details[0].line);
          });
      });
    }
  }, [visible, issueId]);

  const scrollToItem = (line: number) => {
    listRef.current?.scrollToItem(line, 'center');
  };

  const getRowHeight = (index: number) => {
    const lineMinHeight = 30;
    return rowHeights.current[index] || lineMinHeight;
  };

  const setRowHeight = (index: number, size: number) => {
    listRef.current.resetAfterIndex(0);
    rowHeights.current = { ...rowHeights.current, [index]: size };
  };

  const rowRenderer = ({ index, style: rowStyle }: any) => {
    const { lineNum: line, content } = codeFile?.codeContents[index] || {};
    const rowRef: any = useRef({});
    const language = detail.language ?? codeFile.suffix?.split('.')[1] ?? 'plaintext';

    useEffect(() => {
      if (rowRef.current) {
        setRowHeight(index, rowRef.current.clientHeight);
      }
    }, [rowRef]);

    return (
      <div className={style.row} style={rowStyle}>
        <span className={style.codeLine}>{line}</span>
        <div
          ref={rowRef}
          id={line}
          className={cn(style.codeContent, {
            [style[`status-${detail.severity}`]]: (line === 1 && issueLines[0] === 0) || issueLines.includes(line),
          })}
        >
          {
            (
              // 本行有问题 || 问题行为0，即文件问题显示在第一行之前
              (line === 1 && issueLines[0] === 0) || issueLines.includes(line)
            ) && (
              <div className={style.ruleWrapper}>
                <div>
                  <InfoCircle />&nbsp;
                  【{detail.checkrule_real_name}】规则描述：{detail.checkrule_rule_title}
                  {
                    false && (
                      <Button
                        type='link'
                        className={style.ruleDetail}
                        onClick={() => getRuleDetailInfo()}
                      >查看规则</Button>
                    )
                  }
                </div>
                <div className={style.ruleDesc}>{detail.msg}</div>
              </div>
            )
          }
          <Highlight className={language}>
            {content}
          </Highlight>
        </div>
      </div>
    );
  };

  /**
   * 更新 Popover 状态，同时只能展示一个气泡框
   * @param showKey 显示的气泡框的 key
   */
  const setPopStatus = (showKey?: string) => {
    const obj: any = {};
    Object.keys(status).forEach((item) => {
      obj[item] = item === showKey;
    });
    setStatus(obj);
  };

  const getRuleDetailInfo = () => {
    if (isEmpty(ruleDetail)) {
      getRuleDetail(orgSid, teamName, repoId, curSchemeId, detail.checkrule_gid).then((res: any) => {
        setRuleDetail(res);
      });
    }
  };

  // 关闭弹框之后重置状态
  const afterClose = () => {
    setRuleDetail({});
    setPopStatus();
    setCode({});

    // 在弹框关闭之后再请求数据是为了避免列表顺序变化（排序导致），影响弹框中【上/下一个】问题的操作
    if (reloadList) {
      callback();
      setReloadList(false);
    }
  };

  return (
    <Modal
      centered
      title={
        <div className={style.modalTitle}>
          <p>{detail.file_path?.split('/').pop()}</p>
          <Tooltip title='点击跳转新窗口打开详情页'>
            <Link className={style.link} target='_blank' to={`${location.pathname}/${issueId}`}><LinkIcon /></Link>
          </Tooltip>
        </div>
      }
      width={1000}
      visible={visible}
      onCancel={onClose}
      afterClose={afterClose}
      footer={null}
      className={style.antModalIssueModal}
    >
      <link
        rel="stylesheet"
        // href={`https://highlightjs.org/static/demo/styles/monokai-sublime.css`}
        // href={`https://highlightjs.org/static/demo/styles/stackoverflow-light.css`}
        href={'https://highlightjs.org/static/demo/styles/github.css'}
      />
      <div className={style.wrapper}>
        <Operation
          detail={detail}
          status={status}
          params={params}
          issueLines={issueLines}
          scrollToItem={scrollToItem}
          setPopStatus={setPopStatus}
          reloadList={() => setReloadList(true)}
          callback={(data: any) => {
            // 修改成功之后的回调：当前 issue 对应的状态修改
            setDetail({
              ...detail,
              ...data,
            });
          }}
        />
        <div className={style.codeWrapper}>
          {loading ? (
            <Loading />
          ) : (
            <AutoSizer>
              {({ height, width }: any) => (
                <List
                  ref={listRef}
                  height={height}
                  itemCount={codeFile.codeContents?.length || 0}
                  itemSize={getRowHeight}
                  width={width}
                >
                  {rowRenderer}
                </List>
              )}
            </AutoSizer>
          )}
        </div>
      </div>
      <div className={style.issueFooter}>
        <Button onClick={prevIssue} disabled={isFirstIssue}>上一个问题</Button>
        <Button onClick={nextIssue} disabled={isLastIssue}>下一个问题</Button>
      </div>
    </Modal>
  );
};

export default IssueModal;

