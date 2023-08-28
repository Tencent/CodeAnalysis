// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码度量
 */
import React, { useState, useEffect } from 'react';
import { pickBy, isNumber } from 'lodash';

import { message } from 'coding-oa-uikit';

import { getCodeMetrics, updateCodeMetrics } from '@src/services/schemes';
import { CODE_METRIC_DEFAULT_VALUE } from '@src/constant';
import CodeMetricsForm from '@src/components/schemes/code-metrics-form';

interface CodeMetricsProps {
  repoId: number;
  schemeId: number;
  orgSid: string;
  teamName: string;
}

const CodeMetrics = (props: CodeMetricsProps) => {
  const { orgSid, teamName, repoId, schemeId } = props;
  const [data, setData] = useState<any>({});

  useEffect(() => {
    getCodeMetrics(orgSid, teamName, repoId, schemeId).then((response: any) => {
      setData(response);
    });
  }, [orgSid, teamName, repoId, schemeId]);

  const update = (formData: any, info: string) => {
    updateCodeMetrics(orgSid, teamName, repoId, schemeId, {
      ...data,
      ...formData,
    }).then((response: any) => {
      message.success(`${info}成功`);
      setData(response);
    });
  };

  const onFinish = (formData: any) => {
    update({
      ...formData,
      ...CODE_METRIC_DEFAULT_VALUE,
      ...pickBy(formData, key => isNumber(key)),
    }, '更新');
  };

  return (
    <CodeMetricsForm
      data={data}
      onSubmitHandle={onFinish}
      update={update}
    />
  );
};

export default CodeMetrics;
