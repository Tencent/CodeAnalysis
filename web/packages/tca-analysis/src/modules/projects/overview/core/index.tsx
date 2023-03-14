// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览核心概览数据块
 */
import React, { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Row, Col, Tooltip } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';
import classnames from 'classnames';
import { toNumber } from 'lodash';
// 项目内
import CodeLintSVG from '@src/images/codelint.svg';
import CodeLintDisableSVG from '@src/images/codelint-disable.svg';
import CodeCcSVG from '@src/images/codecc.svg';
import CodeCcDisableSVG from '@src/images/codecc-disable.svg';
import CodeDupSVG from '@src/images/codedup.svg';
import CodeDupDisableSVG from '@src/images/codedup-disable.svg';
import { getCCFunIssues } from '@src/services/projects';
import {
  getProjectLintIssueRouter,
  getProjectCCFunIssueRouter,
  getProjectDupIssueRouter,
} from '@src/modules/projects/routes';
import {
  LINT_STATE_TYPE,
  SEVERITY_TYPE,
} from '@src/modules/projects/constants';
import s from '../style.scss';

export interface IConf {
  codelint: boolean;
  codecc: boolean;
  codedup: boolean;
  codecloc: boolean;
}

interface IProps {
  latestLintData: any;
  briefCycData: any;
  briefDupData: any;
  conf: IConf;
}

const Core = (props: IProps) => {
  const { latestLintData, briefCycData, briefDupData, conf } = props;
  const [ccUndealCount, setCcUndealCount] = useState(0);
  const params: any = useParams();
  const { orgSid, teamName } = params;
  const repoId = toNumber(params.repoId);
  const projectId = toNumber(params.projectId);

  useEffect(() => {
    // 获取圈复杂度未处理数据
    getCCFunIssues(orgSid, teamName, repoId, projectId, { limit: 1 }).then((response) => {
      setCcUndealCount(response.count);
    });
  }, [projectId]);

  // 代码检查块
  const renderCodeLint = () => (
    <div className={s.coreItem}>
      <div className={s.tit}>{t('代码检查')}</div>
      <div className={s.codelintItem}>
        <div className={s.undealBox}>
          <div className=" mb-sm">
            <img
              src={conf.codelint ? CodeLintSVG : CodeLintDisableSVG}
              alt="codelint"
            />
          </div>
          <Link
            to={getProjectLintIssueRouter(orgSid, teamName, repoId, projectId, {
              state: LINT_STATE_TYPE.ACTIVE,
            })}
            className={s.aNoStyle}
          >
            <span className={s.specialNum}>{latestLintData.total}</span>{' '}
            <span className=" text-grey-6">个</span>
          </Link>
          <div className=" text-grey-6">未处理问题</div>
        </div>
        <Row style={{ marginBottom: '7px' }}>
          <Col span={6}>
            <Link
              to={getProjectLintIssueRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
                {
                  state: LINT_STATE_TYPE.ACTIVE,
                  severity: SEVERITY_TYPE.FATAL,
                },
              )}
              className={s.aNoStyle}
            >
              <span
                className={s.severityPoint}
                style={{
                  borderColor: 'rgb(229, 27, 40)',
                }}
              />
              <span>
                {latestLintData.fatal} 个致命问题
              </span>
            </Link>
          </Col>
          <Col span={6}>
            <Link
              to={getProjectLintIssueRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
                {
                  state: LINT_STATE_TYPE.ACTIVE,
                  severity: SEVERITY_TYPE.ERROR,
                },
              )}
              className={s.aNoStyle}
            >
              <span
                className={s.severityPoint}
                style={{
                  borderColor: 'rgb(240, 133, 10)',
                }}
              />
              <span>
                {latestLintData.error} 个错误问题
              </span>
            </Link>
          </Col>
          <Col span={6}>
            <Link
              to={getProjectLintIssueRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
                {
                  state: LINT_STATE_TYPE.ACTIVE,
                  severity: SEVERITY_TYPE.WARNING,
                },
              )}
              className={s.aNoStyle}
            >
              <span
                className={s.severityPoint}
                style={{
                  borderColor: 'rgb(59, 147, 250)',
                }}
              />
              <span>
                {latestLintData.warning} 个警告问题
              </span>
            </Link>
          </Col>
          <Col span={6}>
            <Link
              to={getProjectLintIssueRouter(
                orgSid,
                teamName,
                repoId,
                projectId,
                {
                  state: LINT_STATE_TYPE.ACTIVE,
                  severity: SEVERITY_TYPE.INFO,
                },
              )}
              className={s.aNoStyle}
            >
              <span
                className={s.severityPoint}
                style={{
                  borderColor: 'rgb(2, 186, 139)',
                }}
              />
              <span>
                {latestLintData.info} 个提示问题
              </span>
            </Link>
          </Col>
        </Row>
      </div>
    </div>
  );

  // 代码度量块
  const renderCodeMetric = () => (
    <>
      <div className={s.coreItem}>
        <Row align="middle">
          <Col flex="auto">
            <div className={s.tit}>
              {t('圈复杂度')}
              <Tooltip
                title={t('支持C、C++、Java、C#、Dart、JavaScript、Python、Objective-C、Ruby、PHP、Swift、Scala、Go、Lua共14种语言')}
                trigger="hover"
              >
                <QuestionCircle className=" ml-sm text-grey-6" />
              </Tooltip>
            </div>
            <div className="mt-sm">
              <Tooltip
                title={
                  <div>
                    该分支未处理超标方法个数：
                    {briefCycData ? ccUndealCount : '无数据'}
                    <br />
                    该分支所有超标方法个数：
                    {briefCycData ? briefCycData.over_cc_func_count : '无数据'}
                    <br />
                    该分支所有超标方法平均复杂度：
                    {briefCycData
                      ? briefCycData.over_cc_func_average.toFixed(2)
                      : '无数据'}
                    <br />
                    圈复杂度标准：
                    {briefCycData ? briefCycData.min_ccn : '无数据'}
                    <br />
                    <br />
                    注：如设置了过滤其他分支合入问题，则仅上报该分支新增的圈复杂度超标方法
                  </div>
                }
                trigger="hover"
              >
                <Link
                  className={s.aNoStyle}
                  to={getProjectCCFunIssueRouter(
                    orgSid,
                    teamName,
                    repoId,
                    projectId,
                  )}
                >
                  <span className={s.specialNum}>{ccUndealCount}</span>{' '}
                  <span className=" text-grey-6">个未处理</span>
                </Link>
              </Tooltip>
            </div>
          </Col>
          <Col>
            <img
              src={conf.codecc ? CodeCcSVG : CodeCcDisableSVG}
              alt="codecyc"
            />
          </Col>
        </Row>
      </div>
      <div className={classnames(s.coreItem, s.coreItemDup)}>
        <Row align="middle">
          <Col flex="auto">
            <div className={s.tit}>
              {t('代码重复率')}
              <Tooltip
                title={t('支持C、C++、Java、JavaScript、Objective-C、PHP、Python、C#、Ruby、Kotlin、Go、Lua、Swift、Scala共14种语言')}
                trigger="hover"
              >
                <QuestionCircle className=" ml-sm text-grey-6" />
              </Tooltip>
            </div>
            <div className="mt-sm">
              <Link
                className={s.aNoStyle}
                to={getProjectDupIssueRouter(
                  orgSid,
                  teamName,
                  repoId,
                  projectId,
                )}
              >
                <span className={s.specialNum}>
                  {briefDupData ? Math.round(briefDupData.duplicate_rate) : '-'}
                </span>{' '}
                <span className=" text-grey-6">%</span>
              </Link>
            </div>
          </Col>
          <Col>
            <img
              src={conf.codedup ? CodeDupSVG : CodeDupDisableSVG}
              alt="codedup"
            />
          </Col>
        </Row>
      </div>
    </>
  );

  return (
    <div className={s.item}>
      <p className={s.header}>
        <span className={s.tit}>{t('分支概览')}</span>
      </p>
      <div className={s.content}>
        <Row gutter={20}>
          <Col span={16}>{renderCodeLint()}</Col>
          <Col span={8}>{renderCodeMetric()}</Col>
        </Row>
      </div>
    </div>
  );
};

export default Core;
