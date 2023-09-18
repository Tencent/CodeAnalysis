/**
 * 批量编辑节点信息弹框
 */
import React, { useState } from 'react';
import { omit } from 'lodash';
import { Dialog, Loading, MessagePlugin } from 'tdesign-react';
import { t } from '@src/utils/i18n';

import { putMultiNodeProcess } from '@src/services/nodes';
import ProcessTable from '@src/modules/process/process-table';

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
    putMultiNodeProcess({ node_ids: selectedNodes, processes })
      .then(() => {
        MessagePlugin.success('批量配置节点工具进程成功');
        onOk();
      })
      .catch(() => {
        MessagePlugin.error('批量配置节点工具进程失败');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Dialog
      header={t('批量配置工具进程')}
      visible={visible}
      onClose={onCancel}
      width={1000}
      onConfirm={onSubmitProcess}
      confirmBtn={t('保存节点工具进程配置')}
    >
      <Loading loading={loading}>
        <ProcessTable
          processTableData={processTableData}
          setProcessTableData={setProcessTableData}
        />
      </Loading>
    </Dialog>
  );
};

export default MultiProcessModal;
