import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { get } from 'lodash';
import { Table, Checkbox } from 'tdesign-react';

// 项目内
import { getNodeProcess, getProcess } from '@src/services/nodes';

interface ProcessTableProps {
  nodeId?: number;
  processTableData: Array<any>;
  setProcessTableData: (data: any) => void;
}

const ProcessTable = ({ nodeId, processTableData, setProcessTableData }: ProcessTableProps) => {
  const [loading, setLoading] = useState(false);

  const checkedAll = processTableData.every(item => item.checktool.supported);
  const uncheckedAll = processTableData.every(item => !item.checktool.supported);
  const checkedAllIndeterminate = !uncheckedAll && !checkedAll;

  const { t } = useTranslation();

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
    });
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
    });
  };

  useEffect(() => {
    if (nodeId) {
      getNodePorcessList();
    } else {
      getAllPorcessList();
    }
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
      width: 250,
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

  return (
    <Table
    loading={loading}
    rowKey='id'
    data={processTableData}
    columns={columns}
    height={nodeId ? '100%' : '600px'}
    />
  );
};

export default ProcessTable;
