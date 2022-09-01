// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表 - 添加规则
 */
import React, { useEffect, useState } from 'react';
import { useParams, useHistory } from 'react-router-dom';
import qs from 'qs';
import { toNumber, isEmpty, difference, omitBy, omit, cloneDeep } from 'lodash';

import { Table, Button, message } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import { getSchemeRouter } from '@src/utils/getRoutePath';
import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/constant';
import {
  getAllRules,
  addRule,
  getRuleDetail,
  getAllCheckPackages,
  getLanguages,
  getCheckTools,
} from '@src/services/schemes';

import RuleDetail from '../../projects/issues/rule-detail';
import Search from './all-rules-search';

import style from './style.scss';

const { Column } = Table;

const AllRules = () => {
  const params: any = useParams();
  const history = useHistory();
  const { orgSid, teamName, repoId, schemeId } = params;

  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [selectedKeys, setSelectedKeys] = useState([]);
  const [ruleDetailVsb, setRuleDetailVsb] = useState(false);
  const [ruleDetail, setRuleDetail] = useState({});
  const [checkTools, setCheckTools] = useState([]);

  const [allPkgs, setAllPkgs] = useState([]);
  const [languages, setLanguages] = useState([]);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const searchParams: any = omit(query, ['offset', 'limit']);

  const checkProfileId = toNumber(params.checkProfileId);
  const pkgId = toNumber(params.pkgId);

  const getAllPkgs = async () => {
    let pkgs = await getAllCheckPackages(orgSid, teamName, repoId, schemeId);
    pkgs = (pkgs || []).filter((item: any) => !item.disable);
    setAllPkgs(pkgs);
  };

  const getListData = async (
    offset = pageStart,
    limit = pageSize,
    otherParams = searchParams,
  ) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };

    setLoading(true);
    getAllRules(orgSid, teamName, repoId, schemeId, params)
      .then((res: any) => {
        const list = res.results || [];
        history.push(`${window.location.pathname}?${qs.stringify(params)}`);

        setSelectedKeys(list
          .filter((item: any) => item.select_state === 1)
          .map((item: any) => item.id));
        setSelectedRowKeys(list
          .filter((item: any) => item.select_state === 1)
          .map((item: any) => item.id));
        setCount(res.count);
        setList(list);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    getListData();
    getAllPkgs();
    getCheckTools(orgSid, {
      limit: 1000,
      checkprofile_id: checkProfileId,
    }).then((res: any) => {
      setCheckTools(res.results || []);
    });

    (async () => {
      const resLanguages = await getLanguages();
      setLanguages(resLanguages.results || []);
    })();
  }, [pkgId]);

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  const addRules = () => {
    addRule(orgSid, teamName, repoId, schemeId, {
      checkrules: difference(selectedRowKeys, selectedKeys),
    }).then(() => {
      message.success('添加成功');
      getListData(pageStart, pageSize);
    });
  };

  const openRuleDetail = async (ruleId: number) => {
    setRuleDetailVsb(true);
    const res = await getRuleDetail(orgSid, teamName, repoId, schemeId, ruleId);
    setRuleDetail(res);
  };

  return (
    <div className={style.packageRules}>
      <div className={style.header}>
        <span
          className={style.backIcon}
          onClick={() => history.push(`${getSchemeRouter(
            orgSid,
            teamName,
            repoId,
            schemeId,
          )}/check-profiles/${checkProfileId}/pkg/${pkgId}`)
          }
        >
          <ArrowLeft />
        </span>
        <div style={{ flex: 1 }}>
          <h3 className={style.title}>批量添加规则</h3>
        </div>
      </div>

      <Search
        filters={{
          allPkgs,
          languages,
          checkTools,
        }}
        searchParams={cloneDeep(searchParams)}
        loading={loading}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />

      <div className={style.rules}>
        {!isEmpty(difference(selectedRowKeys, selectedKeys)) && (
          <div className={style.operation}>
            <Button type="link" onClick={addRules} style={{ marginRight: 10 }}>
              批量添加 {difference(selectedRowKeys, selectedKeys).length} 条规则
            </Button>
          </div>
        )}
        <Table
          dataSource={list}
          className={style.ruleTable}
          rowKey={(item: any) => item.id}
          rowSelection={{
            selectedRowKeys,
            onChange: keys => setSelectedRowKeys(keys),
            getCheckboxProps: item => ({ disabled: item.select_state === 1 }),
          }}
          pagination={{
            current: Math.floor(pageStart / pageSize) + 1,
            total: count,
            pageSize,
            showSizeChanger: true,
            showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
            onChange: onChangePageSize,
            onShowSizeChange,
          }}
        >
          <Column
            title="规则名称"
            dataIndex="real_name"
            render={(name, data: any) => (
              <p
                className={style.ruleName}
                onClick={() => {
                  openRuleDetail(data.id);
                }}
              >
                {name}
              </p>
            )}
          />
          <Column title="规则概要" dataIndex="rule_title" />
          <Column title="所属工具" dataIndex={['checktool', 'display_name']} />
          <Column title="分类" dataIndex="category_name" />
          <Column title="问题级别" dataIndex="severity_name" />
        </Table>
      </div>
      <RuleDetail
        visible={ruleDetailVsb}
        onClose={() => setRuleDetailVsb(false)}
        data={ruleDetail}
      />
    </div>
  );
};

export default AllRules;
