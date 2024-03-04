// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 问题列表 - 问题详情
 */
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { toNumber, join, get, isEmpty } from 'lodash';
import $ from 'jquery';
import SyntaxHighlighter from 'react-syntax-highlighter';

import Loading from '@src/components/loading';
import SelectBorderless from '@src/components/select-borderless';
import { getIssueDetail, getCodeFile, getProjectDetail } from '@src/services/projects';
import themes from '@src/constant/highlight-theme';

import DetailRight from './detail-right';

import style from './style.scss';

const Detail = () => {
  const params: any = useParams();
  const [detail, setDetail] = useState({}) as any;
  const [code, setCode] = useState({}) as any;
  const [codeLoading, setCodeLoading] = useState(false);
  const [project, setProject] = useState({}) as any;
  const [theme, setTheme] = useState('default-style');
  const [curLine, setCurLine] = useState(-1);
  const { orgSid, teamName } = params;

  let highlightTheme = {};
  try {
    // eslint-disable-next-line
    highlightTheme = require(`react-syntax-highlighter/dist/esm/styles/hljs/${theme}.js`)
      .default;
  } catch {
    highlightTheme = {};
  }

  const issueId = toNumber(params.issueId);
  const projectId = toNumber(params.projectId);
  const repoId = toNumber(params.repoId);

  const issueLine = get(detail, 'issue_details', []).map((item: any) => item.line);

  useEffect(() => {
    (async () => setProject(await getProjectDetail(orgSid, teamName, repoId, projectId)))();
  }, [projectId]);

  useEffect(() => {
    (async () => {
      const detail = await getIssueDetail(orgSid, teamName, repoId, projectId, issueId);
      setDetail(detail);
      try {
        setCodeLoading(true);
        const params: any = {
          path: detail.file_path,
          revision: get(detail, 'issue_details[0].scan_revision'),
        };
        if (detail.is_external) { // 外部代码库需要传url
          params.scm_url = detail.scm_url;
          params.path = detail.real_file_path;
        }
        const codeFile = await getCodeFile(orgSid, teamName, repoId, projectId, params);
        setCode(codeFile);
      } catch (error) {
        console.log(error);
      } finally {
        setCodeLoading(false);
      }
    })();
  }, [issueId]);

  useEffect(() => {
    if (!isEmpty(code) && !isEmpty(issueLine) && !codeLoading) {
      issueLine.forEach((number: number) => {
        const tipsEle = $('<p></p>')
          .css({
            background: '#ff676b',
            color: '#fff',
            'padding-left': '20px',
          })
          .text(`错误原因：${detail.msg}`);

        $(`#code-line-${number}`).after(tipsEle);
      });
      setCurLine(issueLine[0]);
      scrollToLine(issueLine[0]);
    }
  }, [codeLoading]);

  const scrollToLine = (line: number) => {
    const scrollElement = $('pre')[0];
    const anchorElement = $(`#code-line-${line}`)[0];

    if (scrollElement && anchorElement) {
      $(scrollElement)
        .stop()
        .animate(
          {
            scrollTop: anchorElement.offsetTop - 194,
          },
          800,
          'swing',
        );
    }
  };

  return (
        <div className={style.issueDetail}>
            <div className={style.left}>
                <div className={style.header}>
                    <p className={style.fileName}>
                        {detail.file_path?.split('/')?.pop()}
                    </p>
                    <p className={style.path}>路径：{detail.file_path}</p>
                    <p className={style.path}>仓库地址：{detail.is_external ? detail.scm_url : get(project, 'repo.scm_url', '')}</p>
                    <div className={style.themeDropdown}>
                        <SelectBorderless
                            value={theme}
                            data={themes.map(item => ({ value: item.value, text: item.name }))}
                            onChange={(value: any) => setTheme(value)}
                        />
                    </div>
                </div>
                {codeLoading ? (
                    <Loading />
                ) : (
                        <SyntaxHighlighter
                            showLineNumbers
                            language={code.language}
                            style={highlightTheme}
                            wrapLines={true}
                            lineProps={(lineNumber: number) => {
                              const props: any = {};
                              if (issueLine.includes(lineNumber)) {
                                props.style = {
                                  display: 'block',
                                  border: '1px solid #ff676b',
                                };
                                props.id = `code-line-${lineNumber}`;
                              }
                              return { ...props };
                            }}
                        >
                            {code.codeContents
                              ? join(
                                code.codeContents.map((item: any) => item.content),
                                '\n',
                              )
                              : ''}
                        </SyntaxHighlighter>
                )}
            </div>
            <DetailRight
                orgSid={orgSid}
                teamName={teamName}
                repoId={repoId}
                projectId={projectId}
                schemeId={project?.scan_scheme?.id}
                issueId={issueId}
                data={detail}
                curLine={curLine}
                callback={(data: any) => setDetail(data)}
                scrollToLine={(line: number) => {
                  // todo: 同时设置 state 会影响滚动动画效果，考虑用其他动画方式代替
                  // setCurLine(line);
                  scrollToLine(line);
                }}
            />
        </div>
  );
};
export default Detail;
