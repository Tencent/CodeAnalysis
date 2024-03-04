// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分支概览
 */
import React, { useEffect, useState, useRef } from 'react';
import { get, isEmpty } from 'lodash';

// 项目内
import {
  getLatestLintScans,
  getLintScans,
  getCCScans,
  getDupScans,
  getClocScans,
  getMineOverview,
  getScans,
} from '@src/services/projects';
import {
  getLintConfig as getLintConf,
  getCodeMetrics as getMetricConf,
} from '@src/services/schemes';
import s from './style.scss';
import Core, { IConf } from './core';
import Mine from './mine';
import CodeLint from './codelint';
import CodeCC from './codecc';
import CodeDup from './codedup';
import CodeCloc from './codecloc';
import RunJob from './run-job';
import { formatLatestLintData, getBriefCycData, getBriefDupData } from './utils';

interface IProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
  schemeId?: number;
  curTab: string;
}

const Overview = ({ orgSid, teamName, repoId, projectId, schemeId, curTab }: IProps) => {
  const timer = useRef();
  const [latestLintData, setLatestLintData] = useState<any>({});
  const [lintScans, setLintScans] = useState([]);
  const [cycScans, setCycScans] = useState([]);
  const [briefCycData, setBriefCycData] = useState(null);
  const [dupScans, setDupScans] = useState([]);
  const [briefDupData, setBriefDupData] = useState<any>(null);
  const [clocScans, setClocScans] = useState([]);
  const [mineData, setMineData] = useState({});
  const [conf, setConf] = useState<IConf>({
    codelint: false,
    codecc: false,
    codedup: false,
    codecloc: false,
  });
  const [scanHistoryData, setScanHistoryData] = useState({
    latestScan: {},
    count: 0,
  });

  useEffect(() => {
    if (curTab === 'overview') {
      getScanList();
    } else {
      timer.current && clearInterval(timer.current);
    }

    return () => {
      timer.current && clearInterval(timer.current);
    };
  }, [curTab]);

  useEffect(() => {
    // 获取代码检查最新概要数据
    getLatestLintScans(orgSid, teamName, repoId, projectId).then((response) => {
      setLatestLintData(formatLatestLintData(response));
    });
    // 获取代码检查详情数据
    getLintScans(orgSid, teamName, repoId, projectId).then((response) => {
      setLintScans(get(response, 'results', []));
    });
    // 获取圈复杂度详情数据
    getCCScans(orgSid, teamName, repoId, projectId).then((response) => {
      const { results = [] } = response;
      setCycScans(results);
      setBriefCycData(getBriefCycData(results));
    });
    // 获取重复代码详情数据
    getDupScans(orgSid, teamName, repoId, projectId).then((response) => {
      const { results = [] } = response;
      setDupScans(results);
      setBriefDupData(getBriefDupData(results));
    });
    // 获取代码统计详情数据
    getClocScans(orgSid, teamName, repoId, projectId).then((response) => {
      setClocScans(get(response, 'results', []));
    });
    // 获取与我相关概要数据
    getMineOverview(orgSid, teamName, repoId, projectId).then((response) => {
      setMineData(response);
    });

    // 分析任务列表
    getScanList();
  }, [projectId]);

  useEffect(() => {
    // 获取不同分析方案下的代码检查、度量配置
    if (schemeId) {
      getLintConf(orgSid, teamName, repoId, schemeId).then((response) => {
        setConf(state => ({ ...state, codelint: response.enabled }));
      });
      getMetricConf(orgSid, teamName, repoId, schemeId).then((response) => {
        setConf(state => ({
          ...state,
          codecc: response.cc_scan_enabled,
          codedup: response.dup_scan_enabled,
          codecloc: response.cloc_scan_enabled,
        }));
      });
    }
  }, [schemeId]);

  const getScanList = () => {
    getScans(orgSid, teamName, repoId, projectId, null).then((res) => {
      const latestScan = res.results[0] || {};
      if (latestScan.result_code !== null && timer.current) {
        clearInterval(timer.current);
      } else if (latestScan?.result_code === null && !timer.current) {
        timer.current = setInterval(() => {
          getScanList();
        }, 3000) as any;
      }
      setScanHistoryData({
        count: res.count,
        latestScan,
      });
    });
  };

  return (
    <div className={s.overview}>
      {
        !isEmpty(scanHistoryData.latestScan) && (
          <RunJob
            latestScan={scanHistoryData.latestScan}
            count={scanHistoryData.count}
          />
        )
      }
      <Core
        latestLintData={latestLintData}
        briefCycData={briefCycData}
        briefDupData={briefDupData}
        conf={conf}
      />
      <Mine
        mineData={mineData}
        latestLintData={latestLintData}
        briefCycData={briefCycData}
        briefDupData={briefDupData}
      />
      <CodeLint lintScans={lintScans} />
      <CodeCC cycScans={cycScans} />
      <CodeDup dupScans={dupScans} />
      <CodeCloc clocScans={clocScans} />
    </div>
  );
};
export default Overview;
