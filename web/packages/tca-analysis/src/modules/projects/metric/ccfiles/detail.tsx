// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// 圈复杂度文件详情页
import React, { useEffect, useState, useRef } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import cn from 'classnames';
import AutoSizer from 'react-virtualized-auto-sizer';
import Highlight from 'react-highlight';
import { VariableSizeList as List } from 'react-window';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';
import ExclamationTriangle from 'coding-oa-uikit/lib/icon/ExclamationTriangle';

import Loading from '@src/components/loading';
import { getProjectRouter } from '@src/utils/getRoutePath';
import { CC_TYPES } from '../../constants';

import { getCCFileDetail, getCodeFile, getCCFileIssues } from '@src/services/projects';

import style from './style.scss';

const Detail = () => {
  const history = useHistory();
  const listRef: any = useRef({});
  const rowHeights = useRef({});
  // const rowRef: any = useRef({});
  const { org_sid: orgSid, team_name: teamName, repoId, projectId, fileId } = useParams() as any;
  const [codeFile, setCodeFile] = useState({}) as any;
  const [fileInfo, setFileInfo] = useState({}) as any;
  const [issues, setIssues] = useState({
    issueList: [], // issue 列表
    issueLineStart: {}, // 存放所有issue开始行信息
    issueLines: [], // 存放所有issue行
  }) as any;
  const [loading, setLoading] = useState(false);

  const { issueList, issueLineStart, issueLines } = issues;

  useEffect(() => {
    // 获取圈复杂度文件详情
    setLoading(true);
    getCCFileDetail(orgSid, teamName, repoId, projectId, fileId)
      .then((response: any) => {
        setFileInfo(response);
        // 获取代码
        getCodeFile(orgSid, teamName, repoId, projectId, { path: response.file_path })
          .then((res) => {
            setCodeFile(res);
          })
          .finally(() => {
            setLoading(false);
          });
      })
      .catch(() => {
        setLoading(false);
      });

    // 获取问题信息
    getIssues().then((res) => {
      setIssues({
        issueList: res,
        ...detailIssueData(res),
      });
    });
  }, []);

  const getIssues = async (page = 1) => {
    const offset = (page - 1) * 100;
    const response = await getCCFileIssues(orgSid, teamName, repoId, projectId, fileId, {
      limit: 100,
      offset,
    });
    let list = response?.results ?? [];

    if (response.next) {
      list = list.concat(await getIssues(page + 1));
    }
    return list;
  };

  const detailIssueData = (issueList: []) => {
    const issueLineStart = {};
    let issueLines: number[] = [];
    issueList.forEach((item: any) => {
      const { detail } = item;
      if (detail) {
        issueLineStart[detail.start_line_no] = {
          related_modifiers: item.related_modifiers,
          last_modifier: item.last_modifier,
        };
        issueLines = issueLines
          .concat(Array.from(new Array(detail.end_line_no + 1).keys())
            .slice(detail.start_line_no));
      }
    });
    return {
      issueLineStart,
      issueLines,
    };
  };

  const getRowHeight = (index: number) => {
    const lineMinHeight = 35;
    return rowHeights.current[index] || lineMinHeight;
  };

  // 渲染每行显示
  const rowRenderer = ({ index, style: rowStyle }: any) => {
    const { lineNum: line, content } = codeFile?.codeContents[index] || {};
    const rowRef: any = useRef({});
    const language = fileInfo.language ?? codeFile.suffix?.split('.')[1] ?? 'plaintext';


    useEffect(() => {
      if (rowRef.current) {
        setRowHeight(index, rowRef.current.clientHeight);
      }
    }, [rowRef]);

    return (
      <div className={style.codeLineWrapper} style={rowStyle}>
        <span
          className={cn(style.codeLine, {
            [style.isIssue]: issueLines.includes(line),
          })}
        >
          {line}
        </span>
        <div ref={rowRef} id={line} className={style.codeContent}>
          <Highlight className={language}>
            {issueLineStart[line] && (
              <div className={style.issueInfo}>
                <p>
                  <ExclamationTriangle />{' '}
                  该方法独立执行路径条数较多，修复方法请点击上方了解圈复杂度，参考修复建议
                </p>
                <p className={style.modifier}>
                  <span>最近修改人：{issueLineStart[line]?.last_modifier}</span>
                  &nbsp;
                  <span>
                    最近修改过此方法的相关人：
                    {issueLineStart[line]?.related_modifiers}
                  </span>
                </p>
              </div>
            )}
            <div>{content} </div>
          </Highlight>
        </div>
      </div>
    );
  };

  // 设置每行高度
  const setRowHeight = (index: number, size: number) => {
    listRef.current.resetAfterIndex(0);
    rowHeights.current = { ...rowHeights.current, [index]: size };
  };

  const scrollToItem = (line: number) => {
    listRef.current.scrollToItem(line, 'center');
  };

  return (
    <div className={style.fileDetail}>
      <link
        rel="stylesheet"
        href={'https://highlightjs.org/static/demo/styles/github.css'}
      />
      <div className={style.header}>
        <span
          className={style.backIcon}
          onClick={() => history.push(`${getProjectRouter(
            orgSid,
            teamName,
            repoId,
            projectId,
          )}/metric/ccfiles`)
          }
        >
          <ArrowLeft />
        </span>
        <div className={style.fileInfo}>
          <p className={style.fileName}>{fileInfo.file_path}</p>
          <p className={style.desc}>
            <span className={style.ccDesc}>
              超标方法圈复杂度总和：
              <span className={style.red}>{fileInfo.over_func_cc}</span>
            </span>
            <span className={style.ccDesc}>
              超标方法平均圈复杂度：
              <span className={style.red}>{fileInfo.over_cc_avg}</span>
            </span>
            <span className={style.ccDesc}>
              超标方法个数：
              <span className={style.red}>{fileInfo.over_cc_func_count}</span>
            </span>
            <span>最近修改人：{fileInfo.last_modifier}</span>
          </p>
        </div>
      </div>
      <div className={style.contentWrapper}>
        <div className={style.issueList}>
          {issueList.map((item: any) => (
            <div
              key={item.id}
              className={style.issueItem}
              onClick={() => {
                item.detail?.start_line_no
                  && scrollToItem(item.detail?.start_line_no);
                // listRef.current.scrollToItem(item.detail?.start_line_no, 'center')
              }}
            >
              <div>
                <p className={style.funcName}>
                  <span className={style.name}>{item.func_name}</span>
                  <span
                    className={cn(
                      style.status,
                      style[`status-${item.change_type}`],
                    )}
                  >
                    {CC_TYPES[item.change_type]}
                  </span>
                </p>
                <p className={style.desc}>
                  <span className={style.ccDesc}>
                    圈复杂度：<span className={style.red}>{item.ccn}</span>
                  </span>
                  <span>修改人：{item.last_modifier}</span>
                </p>
                <p className={style.desc}>
                  代码行：
                  <span className={style.link}>
                    {item.detail?.start_line_no} - {item.detail?.end_line_no}
                  </span>
                </p>
              </div>
            </div>
          ))}
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
    </div>
  );
};

export default Detail;
