/**
 * 拉取模板模态框
 */

import React, { useState } from 'react';
import { Checkbox, message, Modal } from 'coding-oa-uikit';

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
        <Modal
            title="拉取模板配置"
            width={580}
            visible={visible}
            onCancel={onClose}
            afterClose={() => setData([])}
            onOk={onOk}
        >
            <Checkbox.Group
                value={data}
                onChange={(value: any) => setData(value)}
                style={{ width: '100%' }}
            >
                {Object.entries(config).map(([key, value]: [string, string]) => (
                    <Checkbox value={key} style={{ marginRight: 10 }} key={key}>
                        {value}
                    </Checkbox>
                ))}
            </Checkbox.Group>
        </Modal>
  );
};

export default PullTmplModal;
