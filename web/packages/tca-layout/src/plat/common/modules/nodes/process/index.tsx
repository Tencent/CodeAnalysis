import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import {
  Descriptions,
  Tag,
  Table,
  Row,
  Col,
  Checkbox,
  Button,
  message,
} from 'coding-oa-uikit';
import { CheckboxChangeEvent } from 'coding-oa-uikit/lib/checkbox';
import SaveIcon from 'coding-oa-uikit/lib/icon/Save';
import { omit } from 'lodash';

// 项目内
import { formatDateTime, bytesToSize } from '@tencent/micro-frontend-shared/util';
import NodeStatus from '@tencent/micro-frontend-shared/component/node-status';
import { getNodeProcess, getNode, putNodeProcess } from '@src/services/nodes';

const { Column } = Table;

const Process = () => {
  const { orgSid, nodeId }: any = useParams();
  const [nodeInfo, setNodeInfo] = useState<any>(null);
  const [processTableData, setProcessTableData] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(false);

  const checkedAll = processTableData.every(item => item.checktool.supported);
  const uncheckedAll = processTableData.every(item => !item.checktool.supported);
  const checkedAllIndeterminate = !uncheckedAll && !checkedAll;

  const getNodePorcessRequest = async (id: number) => {
    setLoading(true);
    const process: { [key: string]: any }  = await getNodeProcess(orgSid, id);
    const data = Object.keys(process).map((key: string) => {
      const item = process[key];
      const supported = Object.keys(item).every((k: string) => item[k].supported);
      const unsupported = Object.keys(item).every((k: string) => !item[k].supported);
      return {
        checktool: {
          name: key,
          supported,
          indeterminate: !supported && !unsupported,
        },
        ...process[key],
      };
    });
    setProcessTableData(data);
    setLoading(false);
    return process;
  };

  useEffect(() => {
    (async () => {
      const node = await getNode(orgSid, nodeId);
      setNodeInfo(node);
      await getNodePorcessRequest(nodeId);
    })();
  }, []);

  // 全选、全不选
  const onSelectAllChange = (e: CheckboxChangeEvent) => {
    setProcessTableData((data: Array<any>) => data.map((item: any) => {
      Object.keys(item).forEach((key) => {
        // eslint-disable-next-line no-param-reassign
        item[key].supported = e.target.checked;
        if (key === 'checktool') {
          // eslint-disable-next-line no-param-reassign
          item[key].indeterminate = false;
        }
      });
      return item;
    }));
  };

  // 全选某行，全不选某行
  const onSelectRowAllChange = (e: CheckboxChangeEvent, index: number) => {
    setProcessTableData((data: Array<any>) => {
      const item = data[index];
      Object.keys(item).forEach((key) => {
        item[key].supported = e.target.checked;
        if (key === 'checktool') {
          item[key].indeterminate = false;
        }
      });
      return [...data];
    });
  };

  // 单选
  const onSelectChange = (e: CheckboxChangeEvent, index: number, key: string) => {
    setProcessTableData((data: Array<any>) => {
      const item = data[index];
      item[key].supported = e.target.checked;
      const supported = Object.keys(item).every((k: string) => k === 'checktool' || item[k].supported);
      const unsupported = Object.keys(item).every((k: string) => k === 'checktool' || !item[k].supported);
      item.checktool.indeterminate = !supported && !unsupported;
      item.checktool.supported = supported;
      return [...data];
    });
  };

  const onSaveProcessHandle = () => {
    const process: any = {};
    processTableData.forEach((item: any) => {
      const { name } = item.checktool;
      process[name] = omit(item, ['checktool']);
    });
    putNodeProcess(orgSid, nodeId, process).then(() => {
      message.success(t('已更新该节点进程配置'));
    });
  };

  if (nodeInfo) {
    const { name, manager, related_managers: relatedManagers, addr, nodestatus } = nodeInfo;
    return (
      <div className="px-lg">
        <Descriptions className="py-lg" title={t('节点信息')} bordered>
          <Descriptions.Item label={t('节点名称')}>{name}</Descriptions.Item>
          <Descriptions.Item label={t('负责人')}>{manager}</Descriptions.Item>
          <Descriptions.Item label={t('关注人')}>{relatedManagers.join(', ')}</Descriptions.Item>
          <Descriptions.Item label={t('IP 地址')}>{addr}</Descriptions.Item>
          <Descriptions.Item label={t('节点状态')}>
            <NodeStatus node={nodeInfo} />
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
            <Tag>{`CPU: ${nodestatus?.cpu_usage} % (${nodestatus?.cpu_num}) 核`}</Tag>
            <Tag>
              {t('可用内存:')} {bytesToSize(nodestatus?.mem_free_space)} / {bytesToSize(nodestatus?.mem_space)}
            </Tag>
            <Tag>
              {t('可用硬盘:')} {bytesToSize(nodestatus?.hdrive_free_space)} / {bytesToSize(nodestatus?.hdrive_space)}
            </Tag>
          </Descriptions.Item>
        </Descriptions>
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
        <Table
          className="my-lg"
          loading={loading}
          pagination={false}
          rowKey={(item: any) => item.checktool.name}
          dataSource={processTableData}
        >
          <Column
            title={
              <Checkbox
                checked={checkedAll}
                indeterminate={checkedAllIndeterminate}
                onChange={onSelectAllChange}
              >
                {t('工具')}
              </Checkbox>
            }
            dataIndex="checktool"
            render={(field: any, _: any, index: number) => (
              <Checkbox
                checked={field.supported}
                indeterminate={field.indeterminate}
                onChange={e => onSelectRowAllChange(e, index)}
              >
                {field.name}
              </Checkbox>
            )}
          />
          <Column
            title="analyze"
            dataIndex="analyze"
            render={(field: any, _: any, index: number) => field && (
              <Checkbox
                checked={field.supported}
                onChange={e => onSelectChange(e, index, 'analyze')}
              >
                analyze
              </Checkbox>
            )
            }
          />
          <Column
            title="datahandle"
            dataIndex="datahandle"
            render={(field: any, _: any, index: number) => field && (
              <Checkbox
                checked={field.supported}
                onChange={e => onSelectChange(e, index, 'datahandle')}
              >
                datahandle
              </Checkbox>
            )
            }
          />
          <Column
            title="compile"
            dataIndex="compile"
            render={(field: any, _: any, index: number) => field && (
              <Checkbox
                checked={field.supported}
                onChange={e => onSelectChange(e, index, 'compile')}
              >
                compile
              </Checkbox>
            )
            }
          />
        </Table>
      </div>
    );
  }
  return <></>;
};
export default Process;
