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
  getPackagesRule,
  getCheckPackagesDetail,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  getRulesFilter,
  modifyRule,
  getRuleDetail,
} from '@src/services/template';

import PkgRulesTable from '@src/components/schemes/pkg-details/pkg-rule-table';

const PkgRules = () => {
  const {
    orgSid,
    id: tmplId,
  } = useParams() as any;
  const { pkgId } = useParams() as any;
  const [isSysTmpl, setIsSysTmpl] = useState(true);

  const { data: pkgDetail = {} } = useRequest(getCheckPackagesDetail, {
    defaultParams: [orgSid, tmplId, pkgId],
    refreshDeps: [orgSid, tmplId, pkgId],
  });

  const { data: filters = {} } = useRequest(getRulesFilter, {
    defaultParams: [orgSid, tmplId, pkgId],
    refreshDeps: [orgSid, tmplId, pkgId],
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
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, tmplId, ruleId)}
      pkgDetail={pkgDetail}
      filters={filters}
      getPackagesRule={(filter: any) => getPackagesRule(orgSid, tmplId, pkgId, filter)}
      refreshDeps={[orgSid, tmplId, pkgId]}
      modifyRule={(editRuleInfo: any) => modifyRule(orgSid, tmplId, editRuleInfo)}
      modifyRuleState={(editRuleInfo: any) => modifyRuleState(orgSid, tmplId, editRuleInfo)}
      modifyRuleSeverity={(editRuleInfo: any) => modifyRuleSeverity(orgSid, tmplId, editRuleInfo)}
      delRule={(delRuleInfo: any) => delRule(orgSid, tmplId, delRuleInfo)}
      backLink={`${getTmplRouter(orgSid)}/${tmplId}/codelint`}
    />
  );
};

export default PkgRules;
