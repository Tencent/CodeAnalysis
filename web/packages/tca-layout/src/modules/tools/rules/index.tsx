/**
 * 规则列表
 */
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { toNumber, omit, omitBy } from 'lodash';
import qs from 'qs';
import { Modal, message } from 'coding-oa-uikit';

import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/utils/constant';
import { getRules, getRulesFilters, getLanguages, deleteRule, updateRule, createRule } from '@src/services/tools';
import Search from './search';
import RuleModal from './rule-modal';
import ListComponent from './list-component';

interface RulesProps {
  orgSid: string;
  toolId: number;
  toolDetail: any;
  editable: boolean;
  tab: string;
}

const Rules = ({ orgSid, toolId, toolDetail, editable, tab }: RulesProps) => {
  const query = getQuery();
  const history = useHistory();
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [list, setList] = useState([]);
  const [modal, setModal] = useState({ visible: false, data: {} });
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;

  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getLanguages().then((res) => {
      setLanguages(res.results || []);
    });
  }, []);

  useEffect(() => {
    if (tab === 'rules') {
      getFilters();
      getListData(pageStart, pageSize, {
        ...searchParams,
      });
    }
  }, [orgSid, toolId, tab]);

  const getFilters = () => {
    getRulesFilters(orgSid, toolId).then(res => setFilters(res));
  };

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams, callback?: any) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };

    setLoading(true);
    getRules(orgSid, toolId, params)
      .then((response: any) => {
        // 删除最后一页的最后一条数据
        if (response.results?.length === 0 && pageStart >= pageSize && response.count > 0) {
          getListData(pageStart - pageSize);
          return;
        }
        callback?.(response.results || []);
        setCount(response.count);
        history.replace(`${location.pathname}?${qs.stringify(params)}`);
        setList(response.results || []);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  const delRule = (data: any) => {
    Modal.confirm({
      title: `确定删除规则【 ${data.display_name} 】？`,
      okButtonProps: { danger: true },
      okText: '确定删除',
      onOk: () => {
        deleteRule(orgSid, toolId, data.id).then(() => {
          message.success('删除成功');
          getListData();
        });
      },
    });
  };

  return (
    <>
      <Search
        orgSid={orgSid}
        toolId={toolId}
        loading={loading}
        filters={filters}
        searchParams={searchParams}
        editable={editable}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
        addRule={() => setModal({ visible: true, data: {} })}
      />
      <ListComponent
        data={list}
        loading={loading}
        pager={{ pageSize, pageStart, count }}
        editable={editable}
        onChangePageSize={onChangePageSize}
        onShowSizeChange={onShowSizeChange}
        onDel={delRule}
        onEdit={(data: any) => setModal({
          visible: true,
          data,
        })}
      />
      {
        editable && (
          <RuleModal
            orgSid={orgSid}
            toolId={toolId}
            toolDetail={toolDetail}
            languages={languages}
            visible={modal.visible}
            data={modal.data}
            onClose={() => setModal({ visible: false, data: {} })}
            onAdd={createRule}
            onUpdate={updateRule}
            callback={getListData}
          />
        )
      }
    </>
  );
};

export default Rules;
