// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表 - 添加规则
 */
import React, { useState } from 'react';
import { useRequest } from 'ahooks';
import { useParams } from 'react-router-dom';
import { toNumber, isEmpty, difference, find } from 'lodash';

import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import Header from '@src/components/header';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import { Button, message } from 'tdesign-react';
import RuleTable from '@src/components/rule-table';

import { DEFAULT_PAGER, getAllRuleSearchFields, ALL_PKG_RULE_COLUMN_INDEX } from '@src/constant';
import { getLanguages, getCheckTools } from '@src/services/schemes';

import style from './style.scss';

interface AllRuleTableProps {
  allPkgs: any[];
  refreshDeps: any[];
  getRuleDetail: (ruleId: number) => Promise<any>;
  getAllRules: (filter: any) => Promise<any>;
  addRule: (ruleInfo: any) => Promise<any>;
  backLink: string;
}

const AllRuleTable = ({
  allPkgs,
  refreshDeps,
  getRuleDetail,
  getAllRules,
  addRule,
  backLink,
}: AllRuleTableProps) => {
  const params: any = useParams();

  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [selectedKeys, setSelectedKeys] = useState([]);

  const checkProfileId = toNumber(params.checkProfileId);
  const { orgSid } = params;

  const { data: checkToolData = {} } = useRequest(getCheckTools, {
    defaultParams: [orgSid, {
      limit: 1000,
      checkprofile_id: checkProfileId,
    }],
  });
  const checkTools = checkToolData.results || [];

  const { data: languagesData = {} } = useRequest(getLanguages);
  const languages = languagesData.results || [];

  const filterFields = getAllRuleSearchFields(
    allPkgs,
    checkTools,
    languages,
  );

  const { filter, searchParams } = useURLParams(filterFields);

  const { data = {}, loading, run } = useRequest(() => getAllRules(filter), {
    refreshDeps: [...refreshDeps, filter],
    onSuccess: (result: any, _params: any) => {
      const list = result.results || [];
      setSelectedKeys(list
        .filter((item: any) => item.select_state === 1)
        .map((item: any) => item.id));
      setSelectedRowKeys(list
        .filter((item: any) => item.select_state === 1)
        .map((item: any) => item.id));
      setCount(result.count);
    },
  });

  const addRules = () => {
    addRule({
      checkrules: difference(selectedRowKeys, selectedKeys),
    }).then(() => {
      message.success('添加成功');
      run();
    });
  };

  /**
   * 一键添加指定工具所有规则
   * @param toolId
   */
  const addToolsRules = (toolId: number) => {
    addRule({ checktool: toolId }).then(() => {
      message.success('批量添加成功');
      run();
    });
  };

  return (
    <div className={style.packageRules}>
      <Header
        link={backLink}
        title='批量添加规则'
      />

      <Search
        fields={filterFields}
        searchParams={searchParams}
        className={style.search}
        appendContent={find(checkTools, { id: toNumber(searchParams.checktool) }) && (
          <Button theme='primary' variant="text" onClick={() => addToolsRules(toNumber(searchParams.checktool))}>
            添加 {find(checkTools, { id: toNumber(searchParams.checktool) })?.display_name} 工具的所有规则
          </Button>
        )}
      />

      <div className={style.rules}>
        {!isEmpty(difference(selectedRowKeys, selectedKeys)) && (
          <div className={style.operation}>
            <Button theme='primary' variant='text' onClick={addRules} style={{ marginRight: 10 }}>
              批量添加 {difference(selectedRowKeys, selectedKeys).length} 条规则
            </Button>
          </div>
        )}
        <RuleTable
          orgSid={orgSid}
          tableData={data?.results || []}
          indexs={ALL_PKG_RULE_COLUMN_INDEX}
          count={count}
          loading={loading}
          checkable
          selectedRowKeys={selectedRowKeys}
          setSelectedRowKeys={setSelectedRowKeys}
          getRuleDetail={(ruleId: number) => getRuleDetail(ruleId)}
        />
      </div>
    </div>
  );
};

export default AllRuleTable;
