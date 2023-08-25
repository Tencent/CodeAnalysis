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

import { message } from 'tdesign-react';

import { getTmplMetrics, updateTmplMetrics, syncScheme } from '@src/services/template';
import { CODE_METRIC_DEFAULT_VALUE } from '@src/constant';
import CodeMetricsForm from '@src/components/schemes/code-metrics-form';
import SyncModal from '../sync-modal';

interface CodeMetricsProps {
  orgSid: string;
  tmplId: number;
  isSysTmpl: boolean;
}

const CodeMetrics = (props: CodeMetricsProps) => {
  const { orgSid, tmplId, isSysTmpl } = props;
  const [data, setData] = useState<any>({});
  const [visible, setVisible] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    getTmplMetrics(orgSid, tmplId).then((response: any) => {
      setData(response);
    });
  }, [orgSid, tmplId]);

  const update = (formData: any, info: string, callback?: any) => {
    updateTmplMetrics(orgSid, tmplId, {
      ...data,
      ...formData,
    }).then((response: any) => {
      setData(response);
      if (callback) {
        callback();
      } else {
        message.success(`${info}成功`);
      }
    });
  };

  const onFinish = (submitData: any) => {
    setFormData(submitData);
    setVisible(true);
  };

  const onSync = (keys: any) => {
    update({
      ...formData,
      ...CODE_METRIC_DEFAULT_VALUE,
      ...pickBy(formData, key => isNumber(key)),
    }, '更新', () => {
      if (keys.length === 0) {
        setVisible(false);
        message.success('更新成功');
      }
    });

    if (keys.length > 0) {
      syncScheme(orgSid, tmplId, {
        sync_metric_conf: true,
        schemes: keys,
      }).then(() => {
        message.success('同步成功');
        setVisible(false);
      });
    }
  };

  return (
    <>
      <CodeMetricsForm
        readonly={isSysTmpl}
        data={data}
        onSubmitHandle={onFinish}
        update={update}
      />
      {
        !isSysTmpl && (
          <SyncModal
            tmplId={tmplId}
            visible={visible}
            onClose={() => setVisible(false)}
            onOk={onSync}
          />
        )
      }
    </>
  );
};

export default CodeMetrics;
