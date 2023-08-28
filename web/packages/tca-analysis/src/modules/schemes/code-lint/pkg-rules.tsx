// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表
 */
import React from 'react';
import { useRequest } from 'ahooks';
import { useParams } from 'react-router-dom';
import { getSchemeRouter } from '@src/utils/getRoutePath';
import {
  getPackagesRule,
  getCheckPackagesDetail,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  getRuleDetail,
  getRulesFilter,
  modifyRule,
} from '@src/services/schemes';
import PkgRulesTable from '@src/components/schemes/pkg-details/pkg-rule-table';

const PkgRules = () => {
  const {
    orgSid,
    teamName,
    repoId,
    schemeId,
  } = useParams() as any;
  const { pkgId } = useParams() as any;

  const { data: pkgDetail = {} } = useRequest(getCheckPackagesDetail, {
    defaultParams: [orgSid, teamName, repoId, schemeId, pkgId],
    refreshDeps: [orgSid, teamName, repoId, schemeId, pkgId],
  });

  const { data: filters = {} } = useRequest(getRulesFilter, {
    defaultParams: [orgSid, teamName, repoId, schemeId, pkgId],
    refreshDeps: [orgSid, teamName, repoId, schemeId, pkgId],
  });

  return (
    <PkgRulesTable
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, teamName, repoId, schemeId, ruleId)}
      pkgDetail={pkgDetail}
      filters={filters}
      getPackagesRule={(filter: any) => getPackagesRule(
        orgSid,
        teamName,
        repoId,
        schemeId,
        pkgId,
        filter,
      )}
      refreshDeps={[orgSid, teamName, repoId, schemeId, pkgId]}
      modifyRule={(editRuleInfo: any) => modifyRule(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      modifyRuleState={(editRuleInfo: any) => modifyRuleState(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      modifyRuleSeverity={(editRuleInfo: any) => modifyRuleSeverity(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      delRule={(delRuleInfo: any) => delRule(orgSid, teamName, repoId, schemeId, delRuleInfo)}
      backLink={`${getSchemeRouter(orgSid, teamName, repoId, schemeId)}/codelint`}
    />
  );
};

export default PkgRules;
