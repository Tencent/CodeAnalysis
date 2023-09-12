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

import { getSchemeRouter } from '@src/utils/getRoutePath';
import {
  getAllRules,
  addRule,
  getRuleDetail,
  getAllCheckPackages,
} from '@src/services/schemes';
import AllRuleTable from '@src/components/schemes/pkg-details/all-rule-table';


const AllRules = () => {
  const params: any = useParams();
  const { orgSid, teamName, repoId, schemeId, checkProfileId, pkgId } = params;

  const [allPkgs, setAllPkgs] = useState([]);

  useRequest(getAllCheckPackages, {
    defaultParams: [orgSid, teamName, repoId, schemeId],
    onSuccess: (result: any, _params: any) => {
      const pkgs = result?.filter((item: any) => !item.disable) || [];
      setAllPkgs(pkgs);
    },
  });

  return (
    <AllRuleTable
      allPkgs={allPkgs}
      refreshDeps={[orgSid, teamName, repoId, schemeId]}
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, teamName, repoId, schemeId, ruleId)}
      getAllRules={(filter: any) => getAllRules(orgSid, teamName, repoId, schemeId, filter)}
      addRule={(ruleInfo: any) => addRule(orgSid, teamName, repoId, schemeId, ruleInfo)}
      backLink={params.pkgId
        // 从自定义规则包进入
        ? `${getSchemeRouter(
          orgSid,
          teamName,
          repoId,
          schemeId,
        )}/check-profiles/${checkProfileId}/pkg/${pkgId}`
      // 从已配置规则进入
        : `${getSchemeRouter(
          orgSid,
          teamName,
          repoId,
          schemeId,
        )}/check-profiles/${checkProfileId}/checkrules`}
    />
  );
};

export default AllRules;
