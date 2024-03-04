// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 度量结果
 */
import React, { useState, useEffect } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import { Radio } from 'coding-oa-uikit';

import { getProjectRouter } from '@src/utils/getRoutePath';

import { METRIC_PAGES } from '../constants';

import CCFiles from './ccfiles';
import CCIssues from './ccissues';
import Clocs from './clocs';
import DupFiles from './dupfiles/index';

import style from './style.scss';

interface MetricProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
}

const Metric = (props: MetricProps) => {
  const { page = 'ccfiles' } = useParams() as any;
  const [raidoValue, setRaidoValue] = useState('ccfiles');
  const history = useHistory();

  const { orgSid, teamName, projectId, repoId } = props;

  useEffect(() => {
    switch (page) {
      case 'dupfiles':
        setRaidoValue('dupfiles');
        break;
      case 'clocs':
        setRaidoValue('clocs');
        break;
      default:
        setRaidoValue('ccfiles');
    }
  });

  const renderPage = () => {
    switch (page) {
      case 'ccfiles':
        return (
                    <CCFiles
                        orgSid={orgSid}
                        teamName={teamName}
                        repoId={repoId}
                        projectId={projectId}
                    />
        );
      case 'ccissues':
        return (
                    <CCIssues
                        orgSid={orgSid}
                        teamName={teamName}
                        repoId={repoId}
                        projectId={projectId}
                    />
        );
      case 'dupfiles':
        return (
                    <DupFiles
                        orgSid={orgSid}
                        teamName={teamName}
                        repoId={repoId}
                        projectId={projectId}
                    />
        );
      case 'clocs':
        return (
                    <Clocs
                        orgSid={orgSid}
                        teamName={teamName}
                        repoId={repoId}
                        projectId={projectId}
                    />
        );
      default:
        return (
                    <CCFiles
                        orgSid={orgSid}
                        teamName={teamName}
                        repoId={repoId}
                        projectId={projectId}
                    />
        );
    }
  };

  return (
        <>
            <Radio.Group
                size="small"
                value={raidoValue}
                style={{ marginTop: 16 }}
                onChange={e => history.push(`${getProjectRouter(orgSid, teamName, repoId, projectId)}/metric/${
                  e.target.value
                }`)
                }
            >
                {METRIC_PAGES.map(item => (
                    <Radio.Button key={item.value} value={item.value}>{item.label}</Radio.Button>
                ))}
            </Radio.Group>
            <div className={style.metricContent}>{renderPage()}</div>
        </>
  );
};
export default Metric;
