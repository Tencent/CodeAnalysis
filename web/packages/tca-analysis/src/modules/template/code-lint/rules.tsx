// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表
 */
import React, { useState } from 'react';
import { useRequest } from 'ahooks';
import { useParams } from 'react-router-dom';

import { getTmplRouter } from '@src/utils/getRoutePath';
import {
  getTmplInfo,
  getAllCheckRules,
  getAllCheckRulesFilters,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  modifyRule,
  getRuleDetail,
} from '@src/services/template';

import PkgRulesTable from '@src/components/schemes/pkg-details/pkg-rule-table';

const PkgRules = () => {
  const {
    orgSid,
    id: tmplId,
  } = useParams() as any;
  const [isSysTmpl, setIsSysTmpl] = useState(true);

  const { data: filters = {} } = useRequest(getAllCheckRulesFilters, {
    defaultParams: [orgSid, tmplId],
    refreshDeps: [orgSid, tmplId],
  });

  useRequest(getTmplInfo, {
    defaultParams: [orgSid, tmplId],
    refreshDeps: [orgSid, tmplId],
    onSuccess: (result: any, _params: any) => {
      setIsSysTmpl(result.scheme_key === 'public');
    },
  });

  return (
    <PkgRulesTable
      isSysTmpl={isSysTmpl}
      isAllRule
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, tmplId, ruleId)}
      filters={filters}
      getPackagesRule={(filter: any) => getAllCheckRules(orgSid, tmplId, filter)}
      refreshDeps={[orgSid, tmplId]}
      modifyRule={(editRuleInfo: any) => modifyRule(orgSid, tmplId, editRuleInfo)}
      modifyRuleState={(editRuleInfo: any) => modifyRuleState(orgSid, tmplId, editRuleInfo)}
      modifyRuleSeverity={(editRuleInfo: any) => modifyRuleSeverity(orgSid, tmplId, editRuleInfo)}
      delRule={(delRuleInfo: any) => delRule(orgSid, tmplId, delRuleInfo)}
      backLink={`${getTmplRouter(orgSid)}/${tmplId}/codelint`}
    />
  );
};

export default PkgRules;
