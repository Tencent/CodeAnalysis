// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 路径过滤列表
 */

import React, { useState } from 'react';
import { Table, Modal, message } from 'coding-oa-uikit';

import { SCAN_TYPES, PATH_TYPES } from '../constants';
import { updateScanDir, delScanDir } from '@src/services/schemes';

import UpdateModal from './modal';
import s from './style.scss';

const { Column } = Table;

interface IProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
  data: any[]; // 列表数据
  pager: any;
  getListData: (offset: number, limit: number) => void;
}

const List = (props: IProps) => {
  const { orgSid, teamName, data, pager, repoId, schemeId, getListData } = props;

  const [visible, setVisible] = useState(false);
  const [editData, setEditData] = useState<any>({});
  const { count, pageSize, pageStart } = pager;

  const update = (formData: any) => {
    updateScanDir(orgSid, teamName, repoId, schemeId, editData.id, formData).then(() => {
      message.success('更新成功');
      setVisible(false);
      getListData(pageStart, pageSize);
    });
  };

  const del = (data: any) => {
    Modal.confirm({
      title: '删除过滤路径',
      content: (
        <p>
          确定删除过滤路径 <strong>{data.dir_path}</strong>？
        </p>
      ),
      onOk: () => {
        delScanDir(orgSid, teamName, repoId, schemeId, data.id).then(() => {
          message.success('删除成功');
          getListData(pageStart, pageSize);
        });
      },
    });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  return (
    <>
      <Table
        size="small"
        dataSource={data}
        rowKey={(item: any) => item.id}
        pagination={{
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 个路径，共 ${total} 个`,
          onChange: onChangePageSize,
        }}
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
          render={(type: number) => SCAN_TYPES[type] || type}
        />
        <Column
          title="操作"
          dataIndex="id"
          key="id"
          width={120}
          render={(id: number, data: object) => [
            <a
              key="edit"
              onClick={() => {
                setEditData(data);
                setVisible(true);
              }}
              style={{ color: '#0066ff', fontSize: '13px', marginRight: '20px' }}
            >
              编辑
            </a>,
            <a
              key="del"
              onClick={() => del(data)}
              style={{ color: '#f81d22', fontSize: '13px' }}
            >
              删除
            </a>,
          ]}
        />
      </Table>
      <UpdateModal
        isEditModal={true}
        visible={visible}
        data={editData}
        onHide={() => setVisible(false)}
        onUpdateScanDir={update}
      />
    </>
  );
};

export default List;
