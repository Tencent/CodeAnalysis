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

import { getTmplRouter } from '@src/utils/getRoutePath';
import {
  getAllRules,
  addRule,
  getAllCheckPackages,
  getRuleDetail,
} from '@src/services/template';
import AllRuleTable from '@src/components/schemes/pkg-details/all-rule-table';

const AllRules = () => {
  const params: any = useParams();
  const [allPkgs, setAllPkgs] = useState([]);
  const { orgSid, id: tmplId, pkgId, checkProfileId } = params;

  useRequest(getAllCheckPackages, {
    defaultParams: [orgSid, tmplId],
    onSuccess: (result: any, _params: any) => {
      const pkgs = result?.filter((item: any) => !item.disable) || [];
      setAllPkgs(pkgs);
    },
  });

  return (
    <AllRuleTable
      allPkgs={allPkgs}
      refreshDeps={[orgSid, tmplId]}
      getRuleDetail={(ruleId: number) => getRuleDetail(orgSid, tmplId, ruleId)}
      getAllRules={(filter: any) => getAllRules(orgSid, tmplId, filter)}
      addRule={(ruleInfo: any) => addRule(orgSid, tmplId, ruleInfo)}
      backLink={`${getTmplRouter(orgSid)}/${
        params.id
      }/check-profiles/${checkProfileId}/pkg/${pkgId}`}
    />
  );
};

export default AllRules;
