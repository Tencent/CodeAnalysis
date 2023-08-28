/**
 * 已配置规则列表 - 分析方案/分析方案模板公用
 */
import React from 'react';
import { useRequest } from 'ahooks';
import { useParams } from 'react-router-dom';

import { getSchemeRouter } from '@src/utils/getRoutePath';
import {
  getAllCheckRules,
  getAllCheckRulesFilters,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  getRuleDetail,
  modifyRule,
} from '@src/services/schemes';
import PkgRulesTable from '@src/components/schemes/pkg-details/pkg-rule-table';


const CheckRules = () => {
  const { orgSid, teamName, repoId, schemeId } = useParams<any>();

  const { data: filters = {} } = useRequest(getAllCheckRulesFilters, {
    defaultParams: [orgSid, teamName, repoId, schemeId],
    refreshDeps: [orgSid, teamName, repoId, schemeId],
  });

  return (
    <PkgRulesTable
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, teamName, repoId, schemeId, ruleId)}
      filters={filters}
      getPackagesRule={(filter: any) => getAllCheckRules(
        orgSid,
        teamName,
        repoId,
        schemeId,
        filter,
      )}
      isAllRule
      refreshDeps={[orgSid, teamName, repoId, schemeId]}
      modifyRule={(editRuleInfo: any) => modifyRule(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      modifyRuleState={(editRuleInfo: any) => modifyRuleState(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      modifyRuleSeverity={(editRuleInfo: any) => modifyRuleSeverity(orgSid, teamName, repoId, schemeId, editRuleInfo)}
      delRule={(delRuleInfo: any) => delRule(orgSid, teamName, repoId, schemeId, delRuleInfo)}
      backLink={`${getSchemeRouter(orgSid, teamName, repoId, schemeId)}/codelint`}
    />
  );
};


export default CheckRules;
