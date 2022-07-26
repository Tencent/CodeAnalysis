import React, { useState } from 'react';
import { omit } from 'lodash';
import { message, Modal, Spin } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import ProcessTable from './process/process-table';
import { putMultiNodeProcess } from '@src/services/nodes'

interface MultiProcessModalProps {
  visible: boolean;
  selectedNodes: any;
  onOk: () => void;
  onCancel: () => void;
}

const MultiProcessModal = ({ visible, selectedNodes, onOk, onCancel }: MultiProcessModalProps) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [processTableData, setProcessTableData] = useState<Array<any>>([]);

  const onSubmitProcess = () => {
    setLoading(true);
    const processes: any = {};
    processTableData.forEach((item: any) => {
      const { name } = item.checktool;
      processes[name] = omit(item, ['checktool']);
    });
    putMultiNodeProcess({node_ids: selectedNodes, processes}).then(() => {
      message.success('批量配置节点工具进程成功');
      onOk();
    }).catch(() => {
      message.error('批量配置节点工具进程失败');
    }).finally(() => {
      setLoading(false);
    });
  };

  return (
    <Modal
      forceRender
      title={t('批量配置节点工具进程')}
      visible={visible}
      onOk={onSubmitProcess}
      onCancel={onCancel}
      okText={'保存节点工具进程配置'}
      width={1000}
    >
      <Spin spinning={loading}>
        <ProcessTable
          processTableData={processTableData}
          setProcessTableData={setProcessTableData}
        />
      </Spin>
    </Modal>
  );
};

export default MultiProcessModal;
