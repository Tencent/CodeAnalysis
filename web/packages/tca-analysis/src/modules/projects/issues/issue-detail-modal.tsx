/**
 * issue 弹框
 */

import React, { useState, useEffect, useRef, useMemo } from 'react';
import cn from 'classnames';
import AutoSizer from 'react-virtualized-auto-sizer';
import { VariableSizeList as List } from 'react-window';
import ReactMarkdown from 'react-markdown';
import { findIndex, cloneDeep, find, isEmpty, sortBy } from 'lodash';
import { Modal, Button, Tooltip, Divider } from 'coding-oa-uikit';
import CaretRight from 'coding-oa-uikit/lib/icon/CaretRight';
import CaretDown from 'coding-oa-uikit/lib/icon/CaretDown';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';

import Highlight from '@src/components/react-highlight';
import Copy from '@src/components/copy';
import Loading from '@src/components/loading';
import { getIssueDetail, getCodeFile } from '@src/services/projects';
import { getRuleDetailByName } from '@src/services/schemes';
import { Operation } from './issue-popover';
import style from './style.scss';

/** 定义每行显示最长长度，避免渲染问题 */
const CODE_MAX_CHAR_LENGTH = 1000;

interface IssueModalProps {
  params: any;
  visible: boolean;
  issueId: number | null;
  issuesData: any;
  listLoading: boolean; // 列表数据加载状态
  prevIssue: () => void;
  nextIssue: () => void;
  onClose: () => void;
  callback: () => void;
}

const IssueModal = (props: IssueModalProps) => {
  const {
    params,
    issueId,
    visible,
    issuesData,
    listLoading,
    prevIssue,
    nextIssue,
    onClose,
    callback,
  } = props;
  const [orgSid, teamName, repoId, projectId, schemeId] = params;
  const listRef: any = useRef({});
  const rowHeights = useRef({});
  const [reloadList, setReloadList] = useState(false); // 弹框关闭后是否需要重新请求列表数据
  const [detail, setDetail] = useState<any>({});
  const [loading, setLoading] = useState(false);
  const [codeFile, setCode] = useState<any>({});
  const [isFirstIssue, setIsFirstIssue] = useState(false);
  const [isLastIssue, setIsLastIssue] = useState(false);
  const [status, setStatus] = useState({
    severityPopVsb: false, // 修改严重级别 popover
    authorPopVsb: false, // 修改责任人 popover
    issuePopVsb: false, // 处理问题 popover
    issueLinePopVsb: false, // 查看问题行 popover
    historyPopVsb: false, // 操作记录 popover
  });
  const [expanded, setExpanded] = useState<any>([]); // 标记问题行规则是否展开
  const [ruleDetail, setRuleDetail] = useState<any>({});
  const { list, next, previous } = issuesData;
  const issueLines = detail.issue_details?.map((item: any) => item.line) ?? [];
  const loadingStatus = loading || listLoading;

  // 文件追溯信息
  /* 开源版issue detail没有ID信息，所以用line代替 */
  const [curIssueLine, setCurIssueLine] = useState(null);
  const [showRefers, setShowRefers] = useState(false);
  const issueRefers = useMemo(() => {
    const curIssueDetail = find(detail.issue_details, { line: curIssueLine });
    if (curIssueDetail && !isEmpty(curIssueDetail.issue_refers)) {
      const refers = curIssueDetail.issue_refers?.map((item: any) => {
        // 不在当前文件，跨文件追溯信息展示在 issue detail 行
        if (item.file_path !== detail.file_path) {
          item.isExternal = true;
          item.newline = curIssueDetail.line;
        } else {
          item.isExternal = false;
          item.newline = item.line;
        }
        return item;
      });
      return sortBy(refers, 'seq');
    }
    return [];
  }, [curIssueLine]);

  useEffect(() => {
    // 重置数据
    setExpanded([]);
    setRuleDetail({});

    if (visible && issueId) {
      setCurIssueLine(null);
      setShowRefers(false);

      getIssueDetail(orgSid, teamName, repoId, projectId, issueId).then((res) => {
        const params: any = {
          path: res.file_path,
          revision: res?.issue_details[0]?.scan_revision,
        };
        if (res.is_external) {
          // 外部代码库需要传url
          params.scm_url = res.scm_url;
          params.path = res.real_file_path;
        }
        setDetail(res);
        setLoading(true);
        getCodeFile(orgSid, teamName, repoId, projectId, params)
          .then((response) => {
            setCode(response);
          })
          .finally(() => {
            setLoading(false);
            scrollToItem(res?.issue_details[0]?.line);
          });

        getRuleDetailInfo(res);
      });
    }
  }, [visible, issueId]);

  useEffect(() => {
    if (visible) {
      getIssueBoundary();
    }
  }, [visible, issueId, issuesData]);

  useEffect(() => {
    // 重置数据， 防止在【上/下一个问题】列表需要翻页时出现脏数据展示
    if (listLoading) {
      setCode({});
      setDetail({});
    }
  }, [listLoading]);

  // 判断当前 Issue 是否为第一个/最后一个问题
  const getIssueBoundary = () => {
    const index = findIndex(list, { id: issueId });
    // 如果路由中存在issueId，则index可能为-1，也视作第一个问题
    if (index <= 0 && !previous) {
      // 第一个问题
      setIsFirstIssue(true);
    } else if (isFirstIssue) {
      setIsFirstIssue(false);
    }

    if (index === list.length - 1 && !next) {
      // 最后一个问题
      setIsLastIssue(true);
    } else if (isLastIssue) {
      setIsLastIssue(false);
    }
  };

  const scrollToItem = (line: number) => {
    if (line && listRef.current && listRef.current.scrollToItem) {
      listRef.current.scrollToItem(line, 'center');
    }
  };

  const getRowHeight = (index: number) => {
    const lineMinHeight = 26;
    return rowHeights.current[index] || lineMinHeight;
  };

  const setRowHeight = (index: number, size: number) => {
    listRef.current.resetAfterIndex(0);
    rowHeights.current = { ...rowHeights.current, [index]: size };
  };

  const getCurIssueDetail = (line: number) => find(detail.issue_details, { line });

  const rowRenderer = ({ index, style: rowStyle }: any) => {
    const { lineNum: line, content } = codeFile?.codeContents[index] ?? {};
    const rowRef: any = useRef({});
    const language = detail.language ?? codeFile.suffix?.split('.')[1] ?? 'plaintext';
    const issueIndex = issueLines.indexOf(line);
    const fileError = line === 1 && issueLines[0] === 0; // 文件级警告
    const curIssueDetail = getCurIssueDetail(line);
    const curIssueRefers = issueRefers?.filter((item: any) => item.newline === line);

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
            [style[`status-${detail.severity}`]]:
              (line === 1 && issueLines[0] === 0) || issueLines.includes(line),
            [style.fileError]: line === 1 && issueLines[0] === 0,
          })}
        >
          {// 本行有问题 || 问题行为0，即文件问题显示在第一行之前
          (fileError || issueLines.includes(line)) && (
            <div className={style.ruleWrapper}>
              <div
                className={style.rule}
                onClick={() => {
                  if (issueIndex > -1) {
                    const list = cloneDeep(expanded);
                    list[issueIndex] = !expanded[issueIndex];
                    setExpanded(list);
                  }
                }}
              >
                <span className={style.ruleContent}>
                  {expanded[issueIndex] || fileError ? (
                    <CaretDown />
                  ) : (
                    <CaretRight />
                  )}
                  【{detail.checkrule_real_name}】规则描述：
                  {ruleDetail.rule_title}
                </span>
                <span>
                  {issueIndex !== 0 && !fileError && (
                    <Tooltip
                      title="上一处问题"
                      getPopupContainer={() => document.body}
                    >
                      <Button
                        type="link"
                        icon={<AngleUp />}
                        onClick={(e: any) => {
                          e.stopPropagation();
                          if (issueIndex > -1) {
                            scrollToItem(issueLines[issueIndex - 1]);
                            const nextIssueDetail = getCurIssueDetail(issueLines[issueIndex - 1]);
                            if (nextIssueDetail) {
                              setCurIssueLine(nextIssueDetail.line);
                            }
                          }
                        }}
                      />
                    </Tooltip>
                  )}
                  {issueIndex < issueLines.length - 1 && !fileError && (
                    <Tooltip
                      title="下一处问题"
                      getPopupContainer={() => document.body}
                    >
                      <Button
                        type="link"
                        icon={<AngleDown />}
                        onClick={(e: any) => {
                          e.stopPropagation();
                          if (issueIndex > -1) {
                            scrollToItem(issueLines[issueIndex + 1]);
                            const nextIssueDetail = getCurIssueDetail(issueLines[issueIndex + 1]);
                            if (nextIssueDetail) {
                              setCurIssueLine(nextIssueDetail.line);
                            }
                          }
                        }}
                      />
                    </Tooltip>
                  )}
                </span>
              </div>
              <div className={style.issueMsg}>
                错误原因：{detail.msg}&nbsp;
                {!isEmpty(curIssueDetail?.issue_refers) && (
                    <Button
                      type="link"
                      onClick={() => {
                        setShowRefers(!showRefers);
                        setCurIssueLine(curIssueDetail.line);
                      }}
                    >
                      {showRefers && !isEmpty(curIssueRefers) ? '关闭' : '展开'}追溯
                    </Button>
                )}
                </div>
              {(expanded[issueIndex] || fileError)
                && ruleDetail.checkruledesc?.desc && (
                  <div className={style.ruleDesc}>
                    <h4>规则详细说明</h4>
                    <ReactMarkdown>
                      {ruleDetail.checkruledesc?.desc}
                    </ReactMarkdown>
                  </div>
              )}
            </div>
          )}
          <Highlight className={language}>
            {content.length > CODE_MAX_CHAR_LENGTH
              ? `${content.substring(0, CODE_MAX_CHAR_LENGTH)}...`
              : content}&nbsp;
          </Highlight>
          {
            // 追溯信息
            showRefers && !isEmpty(curIssueRefers) && (
              curIssueRefers.map((item: any) => {
                const index = findIndex(issueRefers, { id: item.id });
                return (
                  <div className={style.issueRefers} key={item.id}>
                    序号 {item.seq}.【 {item.isExternal ? `跨文件问题，文件路径：${item.file_path}，` : ''}第 {line} 行】{item.msg}
                    <span>
                      {index !== -1 && index > 0 && (
                        <Tooltip
                          title="上一步"
                          getPopupContainer={() => document.body}
                        >
                          <Button
                            type="link"
                            icon={<AngleUp />}
                            onClick={(e: any) => {
                              e.stopPropagation();
                              scrollToItem(issueRefers[index - 1]?.newline);
                            }}
                          />
                        </Tooltip>
                      )}
                      {index !== -1 && index < issueRefers.length - 1 && (
                        <Tooltip
                          title="下一步"
                          getPopupContainer={() => document.body}
                        >
                          <Button
                            type="link"
                            icon={<AngleDown />}
                            onClick={(e: any) => {
                              e.stopPropagation();
                              scrollToItem(issueRefers[index + 1]?.newline);
                            }}
                          />
                        </Tooltip>
                      )}
                    </span>
                  </div>
                );
              })
            )
          }
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

  const getRuleDetailInfo = (issueDetail: any) => {
    getRuleDetailByName(
      orgSid,
      teamName,
      repoId,
      schemeId,
      issueDetail.checktool_name,
      issueDetail.checkrule_real_name,
    ).then((res: any) => {
      setRuleDetail(res);
    });
  };

  // 关闭弹框之后重置状态
  const afterClose = () => {
    setRuleDetail({});
    setPopStatus();
    setCode({});
    setShowRefers(false);

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
          <p>
            {detail.file_path?.split('/').pop()}
            <span className={style.modalDesc}>
              文件路径：{detail.file_path}
            </span>
            <Copy text={detail.file_path} className={style.copyIcon} />
          </p>
          {/* todo: 全屏查看issue */}
          {/* <Tooltip title='点击跳转新窗口打开详情页'>
             <Link className={style.link} target='_blank' to={`${location.pathname}/${issueId}`}><LinkIcon /></Link>
           </Tooltip> */}
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
        {/* 显示展示问题所在行 */}
        {/* {
          issueLines?.length > 1 && (
            <div className={style.issueLineBar}>
              <label className={style.lineLabel}>问题所在行：</label>
              {
                issueLines?.map((line: number) => (
                  <a
                    key={line}
                    className={style.line}
                    onClick={() => {
                      scrollToItem(line);
                    }}>第 {line} 行</a>
                ))
              }
            </div>
          )
        } */}
        <div className={style.codeWrapper}>
          {loadingStatus && <Loading className={style.loading} />}
          {!loadingStatus && codeFile.codeContents && (
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
          {!loadingStatus && codeFile.code === -1 && codeFile.cd_error && (
            <div className={style.codeError}>
              <h4>问题所在行</h4>
              {issueLines?.map((line: number) => (
                <a
                  key={line}
                  style={{ display: 'inline-block', minWidth: '88px' }}
                >
                  第 {line} 行
                </a>
              ))}
              <Divider />
              <h4>错误原因</h4>
              <p>{detail.msg}</p>
              <Divider />
              <p>
                代码拉取失败，
                <span className={style.errorDesc}>{codeFile.cd_error}</span>
              </p>
              <p>处理建议</p>
              <p>1. 代码库帐号密码问题。 </p>
              <p>2. 文件格式无法展示 —— 不支持展示.jar等二进制文件。 </p>
              <p>
                3. 代码文件不存在 ——
                可能为本地分析中间代码，请在本地环境下查看代码或者联系管理员定位问题。{' '}
              </p>
            </div>
          )}
        </div>
      </div>
      <div className={style.issueFooter}>
        <Button onClick={prevIssue} disabled={isFirstIssue}>
          上一个问题
        </Button>
        <Button onClick={nextIssue} disabled={isLastIssue}>
          下一个问题
        </Button>
      </div>
    </Modal>
  );
};

export default IssueModal;
