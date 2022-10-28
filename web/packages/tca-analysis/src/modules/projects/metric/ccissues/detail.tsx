// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果 - 圈复杂度 - 方法列表页
 * description  问题详情 <codelint> <圈复杂度>
 */
import React, { useEffect, useState } from 'react';
import $ from 'jquery';
import { Link, useParams } from 'react-router-dom';
import Highlight from 'react-highlight';
import s from './style.scss';
import cn from 'classnames';
import Loading from 'coding-oa-uikit/lib/icon/Loading';
import CloseCircle from 'coding-oa-uikit/lib/icon/CloseCircle';
import { Row, Col, Button, Avatar } from 'coding-oa-uikit';
import AngleLeft from 'coding-oa-uikit/lib/icon/AngleLeft';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

// import { PAGE_KEY, CODE_STYLE_ITEMS } from '../../constants';
import { PAGE_KEY } from '../../constants';
// import LabelDropdown from '@src/components/labeled-dropdown';
import Copy from '@src/components/copy';
import { getProjectRouter } from '@src/utils/getRoutePath';
import {
  getCodeFile,
  getCCIssueDetail,
} from '@src/services/projects';
import { toNumber } from 'lodash';
import { useStateStore } from '@src/context/store';

const CcIssueDetail = () => {
  const { curRepo } = useStateStore();
  // const [codeTheme, setCodeTheme] = useState('default');
  const [codeTheme] = useState('default');
  const [issueDetail, setIssueDetail] = useState({}) as any;
  const [loadingIssueDetail, setLoadingIssueDetail] = useState(true);
  const [codeContents, setCodeContents] = useState([]);
  const [revision, setRevision] = useState('');
  const [loadingCodeContents, setLoadingCodeContents] = useState(false);
  const [getCodeFileDetail, setGetCodeFileDetail] = useState('');
  const [, setCurrentLine] = useState(0);
  const [startLineNum, setStartLineNum] = useState(0);
  const [endLineNum, setEndLineNum] = useState(0);
  const [errorInfo, setErrorInfo] = useState('');
  const offsetLine = 10;

  const params: any = useParams();
  const { orgSid, teamName } = params;
  const repoId = toNumber(params.repoId);
  const projectId = toNumber(params.projectId);

  useEffect(() => {
    // 获取issue详情
    requestIssueDetail();
  }, []);

  const getCodeFileData = (filePath: string, startLineNum: number, endLineNum: number) => {
    // offsetLine = startLineNum - endLineNum;
    const query: any = {
      path: filePath,
      revision,
      start: startLineNum ? startLineNum - offsetLine : 0,
      end: endLineNum ? endLineNum + offsetLine : null,
    };
    setLoadingCodeContents(true);
    getCodeFile(orgSid, teamName, repoId, projectId, query)
      .then((response: any) => {
        setCodeContents(response.codeContents || null);
        setGetCodeFileDetail(response.detail);
      })
      .catch((e) => {
        setErrorInfo(e.msg);
      })
      .finally(() => {
        setLoadingCodeContents(false);
      });
  };

  const requestIssueDetail = () => {
    setLoadingIssueDetail(true);
    getCCIssueDetail(orgSid, teamName, repoId, params.projectId, params.issueId)
      .then((response: any) => {
        const ccIssueDetail = response.detail;
        let currentLine = 0;
        let startLineNum = 0;
        let endLineNum = 0;
        let revision = null;
        if (ccIssueDetail) {
          revision = ccIssueDetail.scan_revision;
          currentLine = ccIssueDetail.start_line_no;
          startLineNum = ccIssueDetail.start_line_no;
          endLineNum = ccIssueDetail.end_line_no;
        }

        setIssueDetail(response);
        setRevision(revision);
        setCurrentLine(currentLine);
        setStartLineNum(startLineNum);
        setEndLineNum(endLineNum);
        getCodeFileData(response.file_path, startLineNum, endLineNum);
      })
      .finally(() => {
        setLoadingIssueDetail(false);
      });
  };

  const renderCCIssueInfo = () => (
    <>
      <div
        className={cn(s.bug_info_content, s.desFs14)}
        style={{ marginTop: '16px', marginBottom: '20px' }}
      >
        <Row>
          <Col xs={4}>圈复杂度</Col>
          <Col xs={4}>{!loadingIssueDetail && issueDetail.ccn}</Col>
        </Row>
      </div>
      <hr className={s.detailHr} />
      <p className={s.title} style={{ marginTop: '16px' }}>
        缺陷位置
      </p>
      <div className={s.bug_info_content}>
        {loadingIssueDetail ? (
          <Loading />
        ) : (
          <>
            <Button
              empty
              type="confirm"
              className={cn(s.hoverBtn, s.hoverFuncBtn)}
              onClick={() => scrollToLine(startLineNum)}
            >
              第{startLineNum}行
            </Button>
            <span className={s.des}>-</span>
            <Button
              empty
              type="confirm"
              style={{ marginLeft: '15px' }}
              className={cn(s.hoverBtn, s.hoverFuncBtn)}
              onClick={() => scrollToLine(endLineNum)}
            >
              第{endLineNum}行
            </Button>
          </>
        )}
      </div>
      {/* todo: remove Row Col */}
      <Row className={s.bug_info_content}>
        <Col xs={4} className={s.desFs14}>
          <p>最近修改</p>
        </Col>
        <Col xs={8}>
          {!loadingIssueDetail && (
            <div className={s.flexBox} style={{ marginBottom: '1px' }}>
              {issueDetail.last_modifier ? (
                <>
                  <Avatar size={24} icon={<UserIcon />} />
                  <span className={cn(s.labelWarpper, s.fs13)}>
                    {issueDetail.last_modifier}
                  </span>
                </>
              ) : (
                <>
                  <span className={s.nullAvatar} />
                  <span className={s.noUser}>未分配</span>
                </>
              )}
            </div>
          )}
        </Col>
      </Row>
      <hr className={s.detailHr} />
      <Row className={s.bug_info_line}>
        <Col xs={4} className={s.des}>
          <p className={s.fs14}>圈复杂度定义</p>
        </Col>
        <Col xs={8}>
          <p>
            数量上表现为独立执行路径条数，也可理解为覆盖所有的可能情况最少使用的测试用例数。
          </p>
        </Col>
      </Row>
      <Row className={s.bug_info_line}>
        <Col xs={4} className={s.des}>
          <p className={s.fs14}>错误原因</p>
        </Col>
        <Col xs={8}>
          <p>
            圈复杂度大说明程序代码可能质量低且难于测试和维护，
            根据经验，程序的可能错误和高的圈复杂度有着很大关系。
          </p>
        </Col>
      </Row>
      <Row className={s.bug_info_line}>
        <Col xs={4} className={s.des}>
          <p className={s.fs14}>修复建议</p>
        </Col>
        <Col xs={8}>
          <p>建议通过 重构方法、简化条件表达式 等手段来降低方法的圈复杂度。</p>
        </Col>
      </Row>
    </>
  );

  const scrollToLine = (lineNum: any) => {
    const scrollElement = document.getElementById('code-container');
    const anchorElement = document.getElementById(`code-line-${lineNum}`);
    if (scrollElement && anchorElement) {
      $(scrollElement)
        .stop()
        .animate(
          {
            scrollTop: anchorElement.offsetTop - 180,
          },
          800,
          'swing',
        );
    }
    setCurrentLine(lineNum);
  };

  const renderCCHighlightCode = (data: any, lineNum: any) => (
    <>
      <Highlight className="">{data.content ? data.content : ' '}</Highlight>
      {lineNum + 2 === startLineNum && (
        <p className={cn(s.show_msg, s.warning_msg)}>
          以下方法独立执行路径条数较多，修复方法请参考右侧修复建议。
          <br />
          <small>最近修改过此方法的人：{issueDetail.related_modifiers}</small>
        </p>
      )}
    </>
  );

  const renderIssueDetail = () => (
    <div>
      {issueDetail ? (
        <div>
          <div className={s.file_name} style={{ marginBottom: '8px' }}>
            {issueDetail.file_path
              ? issueDetail.file_path.replace(/^.*[\\\/]/, '') // eslint-disable-line
              : ''}
            <div className={s.goback_wrapper}>
              <Link
                to={`${getProjectRouter(
                  orgSid,
                  teamName,
                  repoId,
                  projectId,
                )}/metric/ccissues`}
              >
                <span className={s.goback}>
                  <AngleLeft />
                  返回上一级
                </span>
              </Link>
            </div>
          </div>
          <p className={cn(s.des, s.filePath)} style={{ marginBottom: '4px' }}>
            路径：
            {issueDetail.file_path
              ? issueDetail.file_path.split('/').join(' / ')
              : ''}
          </p>
          <p className={cn(s.des, s.filePath)} style={{ marginBottom: '16px' }}>
            <span style={{ marginRight: '4px' }}>
              仓库地址：
              {`${curRepo.scm_url}.${curRepo.scm_type}`}
            </span>
            <Copy text={curRepo.url} copyText={curRepo.url} />
          </p>
        </div>
      ) : (
        <Loading />
      )}
    </div>
  );

  const renderCodeContent = () => {
    const projectPath = window.location.pathname;
    const { origin } = window.location;
    const branchAdmin = `${origin}${projectPath}/code-analysis/${projectId}/job-settings?tab=job-settings`;
    const activeKey = 'cc';

    return (
      <>
        {issueDetail?.issue_details?.[0]?.line === 0 ? (
          <tr className={s.code_tr}>
            <td className={s.line_num}>{issueDetail.issue_details[0].line}</td>
            <td colSpan={3}>
              <Highlight className={s.codelint_error}>Tips: 文件级告警</Highlight>
              <p className={cn(s.show_msg, s.error_msg)}>
                错误原因：{issueDetail?.msg}
              </p>
            </td>
          </tr>
        ) : null}
        {codeContents?.map((data: any, index: any) => (
          <tr key={index} id={`code-line-${data.lineNum}`} className={s.code_tr}>
            <td
              className={cn(
                s.line_num,
                // eslint-disable-next-line
                activeKey === PAGE_KEY.CC
                  ? index + 1 >= startLineNum && index + 1 <= endLineNum
                    ? s.red_line_num
                    : ''
                  : '',
              )}
              key={`line-${index}`}
            >
              {data.lineNum}
            </td>
            <td colSpan={4} key={`content-${index}`}>
              {renderCCHighlightCode(data, index)}
            </td>
          </tr>
        ))}
        {errorInfo && (
          <>
            <div className={s.error_info}>
              <span className={s.cross_icon}>
                <CloseCircle />
              </span>
              <span className={s.error_title}>拉取失败</span>
              <p className={s.error_text}>拉取代码失败，{errorInfo}</p>
            </div>
            <p className={s.error_sug}>处理建议</p>
            <div className={s.sug_tips}>
              <p className={s.sug_item}>
                1. 代码库账号密码问题 -- 前往
                <a href={`${branchAdmin}`} target="_blank" rel="noreferrer">
                  分支项目凭证管理页面
                </a>
                查看
              </p>
              <p className={s.sug_item}>
                2. 文件格式无法展示 -- 不支持展示.jar等二进制文件
              </p>
              <p className={s.sug_item}>
                3. 代码文件不存在 --
                可能为本地分析中间代码，请在本地环境下查看代码或联系管理员定位问题
              </p>
            </div>
          </>
        )}
      </>
    );
  };

  const renderLoading = () => (
    <tr className={s.hideOverflow}>
      <td colSpan={100}>
        <Loading />
        <span className={s.des}>加载中...</span>
      </td>
    </tr>
  );

  const renderCodeContents = () => (
    <>
      {loadingCodeContents ? (
        renderLoading()
      ) : (
        <>
          {renderCodeContent()}
          {getCodeFileDetail !== '' && (
            <tr>
              <td />
              <td>
                <p className={s.des}>{getCodeFileDetail}</p>
              </td>
            </tr>
          )}
        </>
      )}
    </>
  );

  // tslint:disable:no-big-function
  return (
    <>
      <div style={{ paddingTop: '20px', paddingLeft: '30px' }}>
        <link
          rel="stylesheet"
          href={`https://highlightjs.org/static/demo/styles/${codeTheme}.css`}
        />
        <div className={s.codeOperateBar}>
          {renderIssueDetail()}
          <hr />
          <div style={{ height: '26px', marginTop: '6px' }}>
            <div className={s.codeStyleBox}>
              <div className={s.codeStyle} />
              {/* todo: replace */}
              {/* <LabelDropdown
                                multiple
                                value={[codeTheme]}
                                items={CODE_STYLE_ITEMS}
                                label=""
                                defaultValue=""
                                onSelect={(item: any) => setCodeTheme(item.value)}
                            /> */}
            </div>
          </div>
        </div>
        <div className={s.code_container} id="code-container">
          <table className={s.code_table} cellPadding="0" cellSpacing="0">
            <tbody>{renderCodeContents()}</tbody>
          </table>
        </div>
        <div className={s.bug_info_container}>
          <span className={s.title}>问题信息</span>
          {renderCCIssueInfo()}
        </div>
      </div>
    </>
  );
};

export default CcIssueDetail;
