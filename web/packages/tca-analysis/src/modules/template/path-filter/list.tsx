// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 路径过滤列表
 */

import React from 'react';
import { Table } from 'coding-oa-uikit';

import { SCAN_TYPES, PATH_TYPES } from '../../schemes/constants';
import s from './style.scss';

const { Column } = Table;

interface IProps {
  data: any[]; // 列表数据
  pager: any;
  onDel: (id: number) => void;
  onEditModal: (data: object) => void;
  onGetScanDirs: (pageSize: number, pageStart: number) => void;
}

const List = (props: IProps) => {
  const { data, pager, onDel, onEditModal, onGetScanDirs } = props;
  const { count, pageStart, pageSize } = pager;

  const onChangePageSize = (page: number, pageSize: number) => {
    onGetScanDirs(pageSize, (page - 1) * pageSize);
  };

  return (
        <Table
            size="small"
            dataSource={data}
            rowKey={item => item.id}
            pagination={{
              current: Math.floor(pageStart / pageSize) + 1,
              total: count,
              pageSize,
              showTotal: (total, range) => `${range[0]} - ${range[1]} 个路径，共 ${total} 个`,
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
                title='格式'
                dataIndex='path_type'
                key='path_type'
                render={(type: number) => PATH_TYPES[type] || type}

            />
            <Column
                title='分析类型'
                dataIndex='scan_type'
                key='scan_type'
                width={240}
                render={(type: number) => SCAN_TYPES[type] || type}
            />
            <Column
                title='操作'
                dataIndex='id'
                key='id'
                width={120}
                render={(id: number, data: object) => [
                    <a
                        key="edit"
                        onClick={onEditModal.bind(null, data)}
                        style={{ color: '#0066ff', fontSize: '13px', marginRight: '20px' }}
                    >
                        编辑
                    </a>,
                    <a
                        key="del"
                        onClick={onDel.bind(null, id)}
                        style={{ color: '#f81d22', fontSize: '13px' }}
                    >
                        删除
                    </a>,
                ]}
            />
        </Table>

  );
};


export default List;


