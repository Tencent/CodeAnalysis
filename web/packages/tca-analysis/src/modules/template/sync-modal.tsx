// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 同步操作
 */

import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { Table, Modal } from 'coding-oa-uikit';
import { get } from 'lodash';

import { getSchemeBlankRouter } from '@src/utils/getRoutePath';
import { DEFAULT_PAGER } from '@src/constant';
import { getSchemeList } from '@src/services/template';

const { Column } = Table;

interface SyncModalProps {
  onlySync?: boolean;
  tmplId: number;
  visible: boolean;
  onClose: () => void;
  onOk: (keys: any) => void;
}

const SyncModal = (props: SyncModalProps) => {
  const { orgSid, teamName } = useParams() as any;
  const { onlySync, visible, tmplId, onClose, onOk } = props;

  const [list, setList] = useState<any>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [loading, setLoading] = useState(false);
  const [pager, setPager] = useState(DEFAULT_PAGER);
  const { count, pageSize, pageStart } = pager;

  useEffect(() => {
    if (visible) {
      getListData(DEFAULT_PAGER.pageStart);
      setSelectedRowKeys([]);
    }
  }, [visible]);

  const getListData = (offset = pageStart, limit = pageSize) => {
    setLoading(true);
    getSchemeList(orgSid, tmplId, { offset, limit }).then((response) => {
      setPager({
        pageSize: limit,
        pageStart: offset,
        count: response.count,
      });

      setList(response.results || []);
    })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  // const onShowSizeChange = (current: number, size: number) => {
  //     getListData(DEFAULT_PAGER.pageStart, size);
  // };

  return (
    <Modal
      title={`${onlySync ? '' : '保存 & '}同步`}
      width={800}
      // className={style.schemeCreateModal}
      visible={visible}
      onCancel={onClose}
      onOk={() => onOk(selectedRowKeys)}
    >
      <p style={{ marginBottom: 10 }}>
        当前模板下存在以下分析方案，请勾选需要同步的分析方案
        {!onlySync && '；若不勾选，则只修改模板，不进行同步操作'}
      </p>
      <Table
        size='small'
        dataSource={list}
        rowKey={(item: any) => item.id}
        loading={loading}
        // className={style.schemeList}
        rowSelection={{
          selectedRowKeys,
          onChange: keys => setSelectedRowKeys(keys),
        }}
        pagination={{
          size: 'default',
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: true,
          showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
          onChange: onChangePageSize,
          // onShowSizeChange,
        }}
      >
        <Column
          title="分析方案名称"
          dataIndex="name"
          key="name"
          render={(name: string, data: any) => (
            <a target='_blank' href={`${getSchemeBlankRouter(orgSid, teamName, get(data, 'repo.id'), data.id)}/basic`} rel="noreferrer">{name}</a>
          )}
        />
        <Column
          title="所属代码库"
          dataIndex={['repo', 'scm_url']}
          key="repo"
        />
      </Table>
    </Modal>
  );
};

export default SyncModal;
