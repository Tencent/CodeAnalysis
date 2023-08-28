// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 路径过滤列表
 */

import React from 'react';
import { PageInfo, Space, Table, Switch, DialogPlugin } from 'tdesign-react';
import { get } from 'lodash';

import { SCAN_TYPES, PATH_TYPES } from '@src/constant';
import s from './style.scss';

interface PathFilterListProps {
  data: any[]; // 列表数据
  pager?: any;
  isSysPath?: boolean;
  onDel?: (id: number) => void;
  onEditSysPath?: (checked: boolean, id: number) => void;
  onEditModal?: (data: object) => void;
  onGetScanDirs?: (pageStart: number, pageSize: number) => void;
}

const PathFilterList = (props: PathFilterListProps) => {
  const { data, pager = {}, isSysPath, onDel, onEditModal, onEditSysPath, onGetScanDirs } = props;
  const { count, pageStart, pageSize } = pager;

  const onChangePageSize = ({ current, pageSize }: PageInfo) => {
    onGetScanDirs?.((current - 1) * pageSize, pageSize);
  };

  /**
   * 删除路径配置
   */
  const onDelScanDir = (id: any) => {
    const confirmDialog = DialogPlugin.confirm({
      header: '确认删除过滤配置？',
      onConfirm: () => {
        onDel(id);
        confirmDialog.hide();
      },
      onClose: () => {
        confirmDialog.hide();
      },
    });
  };

  const columns = [
    {
      colKey: 'dir_path',
      title: '路径',
      cell: ({ row }: any) => (
        <div className={s.dirPath}>{row?.dir_path}</div>
      ),
    },
    {
      colKey: 'path_type',
      title: '格式',
      width: 200,
      cell: ({ row }: any) => (
        get(PATH_TYPES, row?.path_type, row?.path_type)
      ),
    },
    {
      colKey: 'scan_type',
      title: '分析类型',
      width: 200,
      cell: ({ row }: any) => (
        get(SCAN_TYPES, row?.scan_type, row?.scan_type)
      ),
    },
    {
      colKey: 'ops',
      title: '操作',
      width: 120,
      cell: ({ row }: any) => (isSysPath
        ? <Switch
            value={row.switch}
            onChange={(checked: boolean) => onEditSysPath(checked, row.id)}
          />
        : <Space size='small'>
          <a
            key="edit"
            onClick={onEditModal.bind(null, row)}
          >
            编辑
          </a>
          <a
            key="del"
            onClick={onDelScanDir.bind(null, row?.id)}
            className={s.dangerAction}
          >
            删除
          </a>
        </Space>
      ),
    },
  ];

  return (
    <Table
      size="small"
      data={data}
      columns={columns}
      rowKey='id'
      pagination={!isSysPath && {
        current: Math.floor(pageStart / pageSize) + 1,
        total: count,
        pageSize,
        onChange: onChangePageSize,
      }}
    />
  );
};

export default PathFilterList;
