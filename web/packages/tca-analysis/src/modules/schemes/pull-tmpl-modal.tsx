// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 拉取模板模态框
 */

import React, { useState, useEffect } from 'react';
import { Checkbox, message, Dialog } from 'tdesign-react';

import { pullTmpl } from '@src/services/schemes';

const config = {
  sync_basic_conf: '基础配置',
  sync_lint_rule_conf: '代码检查配置',
  sync_metric_conf: '代码度量配置',
  sync_filter_path_conf: '过滤配置',
};

interface PullTmplModalIProps {
  visible: boolean;
  orgSid: string;
  teamName: string;
  repoId: number;
  schemeId: number;
  onClose: () => void;
  callback?: (id: number | string) => void; // 创建完成之后的回调
}
const PullTmplModal = (props: PullTmplModalIProps) => {
  const { visible, orgSid, teamName, repoId, schemeId, onClose, callback } = props;
  const [data, setData] = useState<any>([]);

  useEffect(() => {
    if (visible) {
      setData([]);
    }
  }, [visible]);

  const onOk = () => {
    pullTmpl(orgSid, teamName, repoId, schemeId, {
      sync_basic_conf: data.includes('sync_basic_conf'),
      sync_lint_rule_conf: data.includes('sync_lint_rule_conf'),
      sync_lint_build_conf: data.includes('sync_lint_rule_conf'),
      sync_metric_conf: data.includes('sync_metric_conf'),
      sync_filter_path_conf: data.includes('sync_filter_path_conf'),
      sync_filter_other_conf: data.includes('sync_filter_path_conf'),
    }).then(() => {
      message.success('同步成功');
      onClose();
      callback?.(schemeId);
    });
  };

  return (
    <Dialog
      header="拉取模板配置"
      width={580}
      visible={visible}
      onClose={onClose}
      onConfirm={onOk}
    >
      <Checkbox.Group
        value={data}
        onChange={(value: any) => setData(value)}
        style={{ width: '100%' }}
        options={Object.entries(config).map(([key, value]: [string, string]) => ({
          label: value,
          value: key,
        }))}
      />
    </Dialog>
  );
};

export default PullTmplModal;
