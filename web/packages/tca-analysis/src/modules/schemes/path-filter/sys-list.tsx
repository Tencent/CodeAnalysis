// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 路径过滤列表
 */

import React from 'react';
import { Table, Switch, message } from 'coding-oa-uikit';


import { SCAN_TYPES, PATH_TYPES } from '../constants';
import { delSysPath, addSysPath } from '@src/services/schemes';
import s from './style.scss';

const { Column } = Table;

interface IProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
  data: any[]; // 列表数据
  getListData: () => void;
}

const SysList = (props: IProps) => {
  const { data, orgSid, teamName, repoId, schemeId, getListData } = props;

  const operation = (checked: boolean, id: number) => {
    const promise = checked
      ? delSysPath(orgSid, teamName, repoId, schemeId, id)
      : addSysPath(orgSid, teamName, repoId, schemeId, id);
    promise.then(() => {
      message.success(`${checked ? '开启' : '关闭'}成功`);
      getListData();
    });
  };

  return (
    <Table
      size="small"
      dataSource={data}
      rowKey={(item: any) => item.id}
      scroll={{ y: 500 }}
      pagination={false}
    >
      <Column
        title="路径"
        dataIndex="dir_path"
        key="dir_path"
        render={(path: string) => <div className={s.dirPath}>{path}</div>}
      />
      <Column
        title="格式"
        dataIndex="path_type"
        key="path_type"
        render={(type: number) => PATH_TYPES[type] || type}
      />
      <Column
        title="过滤类型"
        dataIndex="scan_type"
        key="scan_type"
        width={240}
        render={(type = 2) => SCAN_TYPES[type] || type}
      />
      <Column
        title="操作"
        dataIndex="id"
        key="id"
        width={120}
        render={(id: number, data: any) => (
          <Switch
            checked={data.switch}
            onChange={(checked: boolean) => operation(checked, id)}
          />
        )}
      />
    </Table>
  );
};

export default SysList;
