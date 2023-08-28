// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 过滤配置-入口文件
 */
import React, { useEffect, useState } from 'react';

import { Collapse, message } from 'tdesign-react';

import {
  getSchemeBasic,
  updateSchemeBasic,
} from '@src/services/schemes';

import Path from './path';
import Branch from '@src/components/schemes/path-filter-list/branch';

import style from './style.scss';

const { Panel } = Collapse;

interface PathFilterProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
}

const PathFilter = ({ orgSid, teamName, repoId, schemeId }: PathFilterProps) => {
  const [data, setData] = useState<any>({});
  const [activeKeys, setActiveKeys] = useState<Array<string>>(['path', 'issue']);

  useEffect(() => {
    schemeId && getSchemeBasic(orgSid, teamName, repoId, schemeId).then((response) => {
      setData(response);
    });
  }, [orgSid, teamName, repoId, schemeId]);

  const updateData = (filed: string, value: any) => {
    updateSchemeBasic(orgSid, teamName, repoId, schemeId, {
      ...data,
      [filed]: value,
    }).then((response) => {
      message.success('更新成功');
      setData(response);
    });
  };


  return (
    <Collapse
      borderless
      value={activeKeys}
      className={style.pathFilter}
      onChange={(keys: any) => setActiveKeys(keys)}
    >
      <Panel header="路径过滤" value="path" className={style.panel}>
        <Path orgSid={orgSid} teamName={teamName} repoId={repoId} schemeId={schemeId} />
      </Panel>
      <Panel header="问题过滤" value="issue" className={style.panel}>
        <Branch data={data} updateData={updateData} />
      </Panel>
    </Collapse>
  );
};

export default PathFilter;
