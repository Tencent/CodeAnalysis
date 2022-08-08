import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { omit, get } from 'lodash';
import { Table, Button, Checkbox, MessagePlugin, Tag, Card } from 'tdesign-react';
import { SaveIcon } from 'tdesign-icons-react';
import NodeStatus from '@tencent/micro-frontend-shared/tdesign-component/node-status';
import { formatDateTime, bytesToSize } from '@tencent/micro-frontend-shared/util';

// 项目内
import { getNodeProcess, nodeAPI, putNodeProcess } from '@src/services/nodes';
import s from './style.scss';

const Process = () => {
  const [nodeInfo, setNodeInfo] = useState<any>(null);
  const [processTableData, setProcessTableData] = useState<Array<any>>([]);
  const [loading, setLoading] = useState(false);

  const checkedAll = processTableData.every(item => item.checktool.supported);
  const uncheckedAll = processTableData.every(item => !item.checktool.supported);
  const checkedAllIndeterminate = !uncheckedAll && !checkedAll;

  const { nodeId }: any = useParams();
  const { t } = useTranslation();

  const getNodePorcessRequest = async (id: number) => {
    setLoading(true);
    const process: { [key: string]: any } = await getNodeProcess(id);
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
      const node = await nodeAPI.getDetail(nodeId);
      setNodeInfo(node);
      await getNodePorcessRequest(nodeId);
    })();
  }, []);

  // 全选、全不选
  const onSelectAllChange = (checked: boolean) => {
    setProcessTableData((data: Array<any>) => data.map((item: any) => {
      Object.keys(item).forEach((key) => {
        item[key].supported = checked;
        if (key === 'checktool') {
          item[key].indeterminate = false;
        }
      });
      return item;
    }));
  };

  // 全选某行，全不选某行
  const onSelectRowAllChange = (checked: boolean, index: number) => {
    setProcessTableData((data: Array<any>) => {
      const item = data[index];
      Object.keys(item).forEach((key) => {
        item[key].supported = checked;
        if (key === 'checktool') {
          item[key].indeterminate = false;
        }
      });
      return [...data];
    });
  };

  // 单选
  const onSelectChange = (checked: boolean, index: number, key: string) => {
    setProcessTableData((data: Array<any>) => {
      const item = data[index];
      item[key].supported = checked;
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
    putNodeProcess(nodeId, process).then(() => {
      MessagePlugin.success(t('已更新该节点进程配置'));
    });
  };

  const columns = [
    {
      colKey: 'checktool',
      title: () => (
        <Checkbox
          checked={checkedAll}
          indeterminate={checkedAllIndeterminate}
          onChange={onSelectAllChange}
        >
          {t('工具')}
        </Checkbox>
      ),
      width: 200,
      cell: ({ row, rowIndex }: any) => (
        <Checkbox
          checked={get(row, ['checktool', 'supported'])}
          indeterminate={get(row, ['checktool', 'indeterminate'])}
          onChange={checked => onSelectRowAllChange(checked, rowIndex)}
        >
          {get(row, ['checktool', 'name'])}
        </Checkbox>
      ),
    },
    {
      colKey: 'analyze',
      title: t('analyze'),
      width: 200,
      cell: ({ row, rowIndex }: any) => get(row, 'analyze') && (
        <Checkbox
          checked={get(row, ['analyze', 'supported'])}
          onChange={checked => onSelectChange(checked, rowIndex, 'analyze')}
        >
          analyze
        </Checkbox>
      ),
    },
    {
      colKey: 'datahandle',
      title: t('datahandle'),
      width: 200,
      cell: ({ row, rowIndex }: any) => get(row, 'datahandle') && (
        <Checkbox
          checked={get(row, ['datahandle', 'supported'])}
          onChange={checked => onSelectChange(checked, rowIndex, 'datahandle')}
        >
          datahandle
        </Checkbox>
      ),
    },
    {
      colKey: 'compile',
      title: t('compile'),
      width: 200,
      cell: ({ row, rowIndex }: any) => get(row, 'compile') && (
        <Checkbox
          checked={get(row, ['compile', 'supported'])}
          onChange={checked => onSelectChange(checked, rowIndex, 'compile')}
        >
          compile
        </Checkbox>
      ),
    },
  ];

  if (nodeInfo) {
    const { name, manager, addr, nodestatus } = nodeInfo;
    return (
      <div className="px-lg">
        <Card title={t('节点信息')} className={s.infoCard}>
          <div className={s.infoBox}>
            <div className={s.infoBoxItem}>
              <h1>{t('节点名称')}</h1>
              <span>{name}</span>
            </div>
            <div className={s.infoBoxItem}>
              <h1>{t('负责人')}</h1>
              <span>{manager}</span>
            </div>
            <div className={s.infoBoxItem}>
              <h1>{t('IP 地址')}</h1>
              <span>{addr}</span>
            </div>
            <div className={s.infoBoxItem}>
              <h1>{t('节点状态')}</h1>
              <NodeStatus node={nodeInfo} />
            </div>
          </div>
          <div className={s.singleInfoBox}>
            <div className={s.infoBoxItem}>
              <h1>{t('最近上报心跳')}</h1>
              <span>{formatDateTime(nodeInfo.last_beat_time) || '- -'}</span>
            </div>
            <div className={s.infoBoxItem}>
              <h1>{t('所属标签')}</h1>
              {nodeInfo.exec_tags.map((tag: string) => (
                <Tag key={tag}>{tag}</Tag>
              ))}
            </div>
            <div className={s.infoBoxItem}>
              <h1>{t('节点配置信息')}</h1>
              <Tag>CPU: {nodestatus?.cpu_usage} % ({nodestatus?.cpu_num}) 核</Tag>
              <Tag>
                可用内存: {bytesToSize(nodestatus?.mem_free_space)} / {bytesToSize(nodestatus?.mem_space)}
              </Tag>
              <Tag>
                可用硬盘: {bytesToSize(nodestatus?.hdrive_free_space)} / {bytesToSize(nodestatus?.hdrive_space)}
              </Tag>
            </div>
          </div>
        </Card>
        <Card
          title={t('节点工具进程配置')}
          actions={
            <Button theme="primary" icon={<SaveIcon />} onClick={onSaveProcessHandle}>
              {t('保存节点工具进程配置')}
            </Button>
          }
        >
          <Table
            loading={loading}
            rowKey='id'
            data={processTableData}
            columns={columns}
          />
        </Card>
      </div>
    );
  }
  return <></>;
};
export default Process;
