import React, { useState, useEffect } from 'react';
import { Table, Checkbox } from 'coding-oa-uikit';
import { CheckboxChangeEvent } from 'coding-oa-uikit/lib/checkbox';

// 项目内
import { t } from '@src/i18n/i18next';
import { getNodeProcess, getProcess } from '@src/services/nodes';

const { Column } = Table;

interface ProcessTableProps {
  nodeId?: string | number;
  processTableData: Array<any>;
  setProcessTableData: (data: any) => void;
}

const ProcessTable = ({nodeId, processTableData, setProcessTableData}: ProcessTableProps) => {
  const [loading, setLoading] = useState(false);

  const checkedAll = processTableData.every(item => item.checktool.supported);
  const uncheckedAll = processTableData.every(item => !item.checktool.supported);
  const checkedAllIndeterminate = !uncheckedAll && !checkedAll;

  const getNodePorcessList = () => {
    setLoading(true);
    getNodeProcess(nodeId).then((process: any) => {
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
    })
  };

  const getAllPorcessList = () => {
    setLoading(true);
    getProcess().then((process: any) => {
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
    })
  };

  useEffect(() => {
    if (nodeId) {
      getNodePorcessList();
    } else {
      getAllPorcessList();
    }
  }, []);

  // 全选、全不选
  const onSelectAllChange = (e: CheckboxChangeEvent) => {
    setProcessTableData((data: Array<any>) => data.map((item: any) => {
      Object.keys(item).forEach((key) => {
        item[key].supported = e.target.checked;
        if (key === 'checktool') {
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

  const tableProps = nodeId ? {
    className: "my-lg",
  } : {
    scroll: { y: 800 },
  };

  return (
    <Table
      loading={loading}
      pagination={false}
      rowKey={(item: any) => item.checktool.name}
      dataSource={processTableData}
      {...tableProps}
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
  );
};

export default ProcessTable;
