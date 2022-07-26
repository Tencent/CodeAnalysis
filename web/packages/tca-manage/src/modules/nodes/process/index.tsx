import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Descriptions,
  Tag,
  Row,
  Col,
  Spin,
  Button,
  message,
} from 'coding-oa-uikit';
import SaveIcon from 'coding-oa-uikit/lib/icon/Save';
import { omit } from 'lodash';
import Loading from 'coding-oa-uikit/lib/icon/Loading'
import Stop from 'coding-oa-uikit/lib/icon/Stop'
import ExclamationCircle from 'coding-oa-uikit/lib/icon/ExclamationCircle'
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle'

// 项目内
import { bytesToSize, formatDateTime } from '@src/utils';
import { t } from '@src/i18n/i18next';
import { getNode, putNodeProcess } from '@src/services/nodes';

// 模块内
import { STATUS_ENUM, STATE_ENUM } from '../constants';
import ProcessTable from './process-table';

const Process = () => {
  const { nodeId }: any = useParams();
  const [nodeInfo, setNodeInfo] = useState<any>(null);
  const [processTableData, setProcessTableData] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getNode(nodeId).then((response: any) => {
      setNodeInfo(response);
      setLoading(false);
    });
  }, []);

  const onSaveProcessHandle = () => {
    const process: any = {};
    processTableData.forEach((item: any) => {
      const { name } = item.checktool;
      process[name] = omit(item, ['checktool']);
    });
    putNodeProcess(nodeId, process).then(() => {
      message.success(t('已更新该节点进程配置'));
    });
  };

  if (nodeInfo) {
    const { name, manager, related_managers, addr, enabled, state } = nodeInfo;
    let nodeStatusRender = <Tag icon={<ExclamationCircle />} color='warning'>{t('离线')}</Tag>
    if (enabled === STATUS_ENUM.ACTIVE && state === STATE_ENUM.BUSY) {
      nodeStatusRender = <Tag icon={<Loading />} color='processing'>{t('运行中')}</Tag>
    } else if (enabled === STATUS_ENUM.ACTIVE) {
      nodeStatusRender = <Tag icon={<DotCircle />} color='success'>{t('在线')}</Tag>
    } else if (enabled === STATUS_ENUM.DISACTIVE) {
      nodeStatusRender = <Tag icon={<Stop />}>{t('失效')}</Tag>
    }
    return (
      <div className="px-lg">
        <Spin spinning={loading}>
          <Descriptions className="py-lg" title={t('节点信息')} bordered>
            <Descriptions.Item label={t('节点名称')}>{name}</Descriptions.Item>
            <Descriptions.Item label={t('负责人')}>{manager}</Descriptions.Item>
            <Descriptions.Item label={t('关注人')}>{related_managers.join(', ')}</Descriptions.Item>
            <Descriptions.Item label={t('IP 地址')}>{addr}</Descriptions.Item>
            <Descriptions.Item label={t('节点状态')}>
              {nodeStatusRender}
            </Descriptions.Item>
            <Descriptions.Item label={t('最近上报心跳')}>
              {formatDateTime(nodeInfo.last_beat_time) || '- -'}
            </Descriptions.Item>
            <Descriptions.Item span={3} label={t('所属标签')}>
              {nodeInfo.exec_tags.map((tag: string) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </Descriptions.Item>
            <Descriptions.Item span={3} label={t('节点配置信息')}>
              <Tag>CPU: {nodeInfo.nodestatus?.cpu_usage} % ({nodeInfo.nodestatus?.cpu_num}) 核</Tag>
              <Tag>可用内存: {bytesToSize(nodeInfo.nodestatus?.mem_free_space)} / {bytesToSize(nodeInfo.nodestatus?.mem_space)} </Tag>
              <Tag>可用硬盘: {bytesToSize(nodeInfo.nodestatus?.hdrive_free_space)} / {bytesToSize(nodeInfo.nodestatus?.hdrive_space)}</Tag>
            </Descriptions.Item>
          </Descriptions>
        </Spin>
        <Row>
          <Col flex="none">
            <span className="fs-16 text-weight-bold">{t('节点工具进程配置')}</span>
          </Col>
          <Col flex="auto" className="text-right">
            <Button type="primary" icon={<SaveIcon />} onClick={onSaveProcessHandle}>
              {t('保存节点工具进程配置')}
            </Button>
          </Col>
        </Row>
        <ProcessTable
          nodeId={nodeId}
          processTableData={processTableData}
          setProcessTableData={setProcessTableData}
        />
      </div>
    );
  }
  return <></>;
};
export default Process;
