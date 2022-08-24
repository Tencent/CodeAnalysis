import React from 'react';
import { useTranslation } from 'react-i18next';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { Tag } from 'tdesign-react';

import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import { get, concat } from 'lodash';

// 项目内
import { getToolRouter } from '@plat/util';
import { RuleSeverityEnum, RuleSeverityInvertEnum, RULE_SEVERITY_CHOICES } from '@src/constant';

// const { Column } = Table;

interface RuleTableProps {
  /** 表格数据 */
  tableData: any;
  /** 列数据在表格数据中对应的路径集合 */
  indexs: any;
  /** 加载状态 */
  loading: boolean;
  /** 数据总数 */
  count: number;
  /** 是否可编辑规则 */
  editable?: boolean;
  /** 是否可选择规则 */
  checkable?: boolean;
  /** 选中规则的ID列表 */
  selectedRowKeys?: any;
  /** 选则规则回调函数 */
  setSelectedRowKeys?: (selectedKeys: any) => void;
  /** 编辑规则回调函数 */
  editRule?: (ruleInfo: any) => void;
}

const RuleTable = ({
  tableData,
  indexs,
  count,
  loading,
  editable = false,
  checkable = false,
  selectedRowKeys = null,
  setSelectedRowKeys = null,
  editRule = null }: RuleTableProps) => {
  const { t } = useTranslation();
  const { currentPage, pageSize } = useURLParams();

  const onSelectChange = (selectedKeys: any) => {
    setSelectedRowKeys(selectedKeys);
  };

  const checkColumn = {
    colKey: 'row-select',
    type: 'multiple',
    checkProps: ({ row }: any) => ({
      disabled: get(row, 'select_state') === 2,
      checked: get(row, 'select_state') === 2 || selectedRowKeys.indexOf(row?.id) !== -1,
    }),
    width: 50,
  };

  const editColumn = {
    colKey: 'ops',
    title: t('操作'),
    width: 100,
    cell: ({ row }: any) => (
      <a
        onClick={() => editRule(row)}
      >
        {t('编辑')}
      </a>
    ),
  };

  const infoColumns = [
    {
      colKey: indexs.rule_display_name,
      title: t('规则名称'),
      width: 300,
      cell: ({ row }: any) => (<>
          <span className="link-name text-weight-bold">{get(row, indexs.rule_display_name)}</span>
          {get(row, indexs.rule_title) && <p className='mt-sm fs-12 text-grey-6'>{get(row, indexs.rule_title)}</p>}
        </>),
    },
    {
      colKey: indexs.tool_display_name,
      title: t('所属工具'),
      width: 200,
      cell: ({ row }: any) => (
        <a
          className="link-name"
          href={getToolRouter(get(row, 'checktool'))}
          target='_blank'
          rel="noopener noreferrer"
        >
          {get(row, indexs.tool_display_name)}{get(row, 'checktool').scope === 1 && <span className='fs-12'>（私有）</span>}
        </a>),
    },
    {
      colKey: indexs.rule_severity,
      title: t('级别'),
      width: 100,
      cell: ({ row }: any) => (<Tag className={RuleSeverityInvertEnum[get(row, indexs.rule_severity)].toLowerCase()}>
        {RULE_SEVERITY_CHOICES[get(row, indexs.rule_severity) as RuleSeverityEnum]}
      </Tag>),
    },
    {
      colKey: indexs.rule_category_name,
      title: t('类别'),
      width: 100,
    },
    {
      colKey: indexs.rule_support_language,
      title: t('语言'),
      width: 100,
      cell: ({ row }: any) => (get(row, indexs.rule_support_language).join() || '通用'),
    },
    {
      colKey: 'status',
      title: '状态',
      width: 100,
      cell: ({ row }: any) => {
        switch (get(row, indexs.rule_status)) {
          case 1:
            return <Tag theme="success" variant="light">生效中</Tag>;
          case 2:
            return <Tag theme="danger" variant="light">已屏蔽</Tag>;
          case false:
            return <Tag theme="success" variant="light">活跃</Tag>;
          case true:
            return <Tag theme="danger" variant="light">失效</Tag>;
          default:
            return <Tag>未知</Tag>;
        }
      },
    },
    {
      colKey: indexs.rule_owner,
      title: t('负责人'),
      width: 120,
    },
  ];

  const getColumns = () => {
    let columns = infoColumns;
    if (checkable) columns = concat(checkColumn, columns);
    if (editable) columns = concat(columns, editColumn);
    return columns;
  };

  return (
    <Table
      rowKey='id'
      data={tableData}
      columns={getColumns()}
      selectedRowKeys={selectedRowKeys}
      onSelectChange={onSelectChange}
      loading={loading}
      pagination={{
        current: currentPage,
        total: count,
        pageSize,
      }}
    />
  );
};

export default RuleTable;
