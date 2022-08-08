// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 圈复杂度 - 方法列表详情
 */
import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import cn from 'classnames';
import AutoSizer from 'react-virtualized-auto-sizer';
import Highlight from 'react-highlight';
import { VariableSizeList as List } from 'react-window';
import { Modal, Button, Tooltip } from 'coding-oa-uikit';
import InfoCircle from 'coding-oa-uikit/lib/icon/InfoCircle';
import LinkIcon from 'coding-oa-uikit/lib/icon/Link';

import PositionIcon from '@src/images/position.svg';
import { getCodeFile, getCCIssueDetail } from '@src/services/projects';
import Loading from '@src/components/loading';

import style from './style.scss';

interface IssueModalProps {
  params: any;
  visible: boolean;
  issueId: number;
  isFirstIssue: boolean;
  isLastIssue: boolean;
  prevIssue: () => void;
  nextIssue: () => void;
  onClose: () => void;
  callback: () => void;
}

const IssueModal = (props: IssueModalProps) => {
  const { params, visible, issueId, isFirstIssue, isLastIssue, prevIssue, nextIssue, onClose } = props;
  const [orgSid, teamName, repoId, projectId] = params;
  const listRef: any = useRef({});
  const rowHeights = useRef({});
  const [detail, setDetail] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [codeFile, setCode] = useState<any>({});

  useEffect(() => {
    if (visible && issueId) {
      getCCIssueDetail(orgSid, teamName, repoId, projectId, issueId).then((res) => {
        setDetail({
          ...res,
          ...res.detail,
        });
        setLoading(true);
        getCodeFile(orgSid, teamName, repoId, projectId, {
          path: res.file_path,
        }).then((file) => {
          setCode(file);
        })
          .finally(() => {
            setLoading(false);
            scrollToItem(res?.detail?.start_line_no);
          });
      });
    }
  }, [visible, issueId]);

  // 关闭弹框之后重置状态
  const afterClose = () => {
    setCode({});
  };

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
        <span className={cn(style.codeLine)}>{line}</span>
        <div
          ref={rowRef}
          id={line}
          className={cn(style.codeContent, {
            [style.issueCode]: line >= detail.start_line_no && line <= detail.end_line_no,
          })}
        >
          {
            line === detail.start_line_no && (
              <div className={style.ruleWrapper}>
                <InfoCircle />&nbsp;
                最近修改过此方法的相关人：{detail.last_modifier}
              </div>
            )
          }
          <Highlight className={language}>
            <div>{content} </div>
          </Highlight>
        </div>
      </div>
    );
  };


  return (
    <Modal
      centered
      title={
        <div className={style.modalTitle}>
          <p>{detail.func_name}</p>
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
      <div className={style.wrapper}>
        <div className={style.operationWrapper}>
          <div>
            <span>
              圈复杂度：<span className={style.ccn}>{detail.ccn}</span>
            </span>
            <span className="ml-12">
              方法行：
              <a onClick={() => scrollToItem(detail?.start_line_no)}>{detail.start_line_no}</a>&nbsp;-&nbsp;
              <a onClick={() => scrollToItem(detail?.end_line_no)}>{detail.end_line_no}</a>
            </span>
          </div>
          <div>
            <Tooltip
              title={
                <div>
                  <h3 style={{ color: '#fff' }}>圈复杂度说明</h3>
                  <p>定义：数量上表现为独立执行路径条数，也可理解为覆盖所有的可能情况最少使用的测试用例数。 </p>
                  <p>关键：圈复杂度大说明程序代码可能质量低且难于测试和维护，根据经验，程序的可能错误和高的圈复杂度有着很大关系。 </p>
                  <p>修复建议：建议通过重构方法、简化条件表达式等手段来降低方法的圈复杂度。 </p>
                </div>
              }
            >
              <a className="mr-12">了解圈复杂度</a>
            </Tooltip>
            <Tooltip title='定位方法'>
              <Button
                shape="circle"
                icon={<img src={PositionIcon} />}
                disabled={loading}
                onClick={() => {
                  scrollToItem(detail?.start_line_no);
                }}
              />
            </Tooltip>
          </div>
        </div>
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
        <Button onClick={prevIssue} disabled={loading || isFirstIssue}>上一个方法</Button>
        <Button onClick={nextIssue} disabled={loading || isLastIssue}>下一个方法</Button>
      </div>
    </Modal>
  );
};

export default IssueModal;
