// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 处理问题模态框
 */

import React, { useState } from 'react';

import { Modal, Radio, Switch, Tooltip } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';

interface HandleIssueModalProps {
  visible: boolean;
  onClose: () => void;
  onOk: (data: any) => void;
}

const HandleIssueModal = (props: HandleIssueModalProps) => {
  const [type, setType] = useState();
  const [scope, setScope] = useState(1);
  const { visible, onClose, onOk } = props;

  const onReset = () => {
    setType(undefined);
    setScope(1);
    onClose();
  };

  return (
        <Modal
            title="标记处理"
            visible={visible}
            onCancel={onReset}
            onOk={() => onOk({ resolution: type, scope })}
        >
            <p className="mb-12">请选择处理问题方式，提交后问题状态将置为已处理</p>
            <Radio.Group
                value={type}
                onChange={(e) => {
                  if (e.target.value === 1) {
                    setScope(1);
                  }
                  setType(e.target.value);
                }}
            >
                <Radio value={1}>已修复</Radio>
                <Radio value={2}>无需修复</Radio>
                <Radio value={3}>误报</Radio>
            </Radio.Group>
            {
                (type === 2 || type === 3) && (
                    <p style={{ marginTop: 10 }}>
                        <Switch
                            checked={scope === 2}
                            onChange={(checked) => {
                              setScope(checked ? 2 : 1);
                            }}
                        />&nbsp;全局忽略
                        （非必选项，谨慎操作）
                        <Tooltip title="开启全局忽略后，代码库内其他分析项目扫出相同问题会直接复用当前忽略方式，请谨慎操作！">
                            <QuestionCircle />
                        </Tooltip>
                    </p>
                )
            }
        </Modal>
  );
};

export default HandleIssueModal;
