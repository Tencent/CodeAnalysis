/**
 * 规则列表
 */
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory } from 'react-router-dom';
import { omitBy } from 'lodash';
import qs from 'qs';
import { Modal, message, Button } from 'coding-oa-uikit';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import Search from '@tencent/micro-frontend-shared/component/search';

// 项目内
import { DEFAULT_PAGER } from '@src/constant';
import { getRules, getRulesFilters, getLanguages, deleteRule, updateRule, createRule } from '@src/services/tools';
import RuleModal from './rule-modal';
import ListComponent from './list-component';
import { getRuleSearchFields, getRuleFilterFields } from '../../constants';

interface RulesProps {
  orgSid: string;
  toolId: number;
  toolDetail: any;
  editable: boolean;
  tab: string;
}

const Rules = ({ orgSid, toolId, toolDetail, editable, tab }: RulesProps) => {
  const history = useHistory();
  const { t } = useTranslation();
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({});
  const [list, setList] = useState([]);
  const [modal, setModal] = useState({ visible: false, data: {} });
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const { searchParams, pageSize, pageStart } = useURLParams(getRuleFilterFields(filters));

  useEffect(() => {
    getLanguages().then(({ results = [] }: any) => {
      setLanguages(results);
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
        history.push(`${location.pathname}?${qs.stringify(params)}`);
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
      title: t(`确定删除规则【 ${data.display_name} 】？`),
      okButtonProps: { danger: true },
      okText: t('确定删除'),
      onOk: () => {
        deleteRule(orgSid, toolId, data.id).then(() => {
          message.success(t('删除成功'));
          getListData();
        });
      },
    });
  };

  return (
    <>
      <Search loading={loading} route={false}
        fields={getRuleSearchFields(filters)}
        searchParams={searchParams}
        callback={(params) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
        extraContent={editable && <Button type='primary' onClick={() => {
          setModal({ visible: true, data: {} });
        }}>{t('添加规则')}</Button>}
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
