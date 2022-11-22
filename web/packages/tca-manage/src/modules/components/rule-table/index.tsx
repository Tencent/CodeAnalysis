import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Tag } from 'tdesign-react';
import { get, concat, isEmpty, slice } from 'lodash';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { getToolRouter } from '@plat/util';
import { RuleSeverityEnum, RuleSeverityInvertEnum, RULE_SEVERITY_CHOICES } from '@src/constant';
import RuleDetailDrawer from './rule-detail-drawer';

interface RuleTableProps {
  /** 表格数据 */
  tableData: any;
  /** 列数据在表格数据中对应的路径集合 */
  indexs: any;
  /** 加载状态 */
  loading: boolean;
  /** 数据总数 */
  count: number;
  /** 是否分析方案内自定义规则 */
  isTmplPkgRule?: boolean;
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
  isTmplPkgRule = false,
  editable = false,
  checkable = false,
  selectedRowKeys = null,
  setSelectedRowKeys = null,
  editRule = null }: RuleTableProps) => {
  const { t } = useTranslation();
  const { currentPage, pageSize } = useURLParams();
  const [ruleDetailVisible, setRuleDetailVisible] = useState<boolean>(false);
  const [ruleDetail, setRuleDetail] = useState<any>({});

  const onSelectChange = (selectedKeys: any) => {
    setSelectedRowKeys(selectedKeys);
  };

  const checkColumn = {
    colKey: 'row-select',
    type: 'multiple',
    checkProps: ({ row }: any) => ({
      disabled: get(row, 'select_state') === 2 || get(row, 'select_state') === 1,
      checked: get(row, 'select_state') === 2 || get(row, 'select_state') === 1 || selectedRowKeys.indexOf(row?.id) !== -1,
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

  const customizeColumn = [
    {
      colKey: 'isTmplPkgRuleSeverity',
      title: t('自定义级别'),
      width: 100,
      cell: ({ row }: any) => (!isEmpty(row?.custom_packagemap) && <Tag className={RuleSeverityInvertEnum[get(row, 'custom_packagemap.0.severity')]?.toLowerCase()}>
        {RULE_SEVERITY_CHOICES[get(row, 'custom_packagemap.0.severity') as RuleSeverityEnum]}
      </Tag>),
    },
    {
      colKey: 'isTmplPkgRuleState',
      title: t('自定义状态'),
      width: 100,
      cell: ({ row }: any) => {
        if (isEmpty(row?.custom_packagemap)) {
          return;
        }
        switch (get(row, 'custom_packagemap.0.state')) {
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
  ];

  const infoColumns = [
    {
      colKey: indexs.rule_display_name,
      title: t('规则名称'),
      width: 300,
      cell: ({ row }: any) => (<>
          <a className="text-weight-bold" onClick={() => {
            if (isTmplPkgRule && !isEmpty(row?.custom_packagemap)) {
              setRuleDetail(get(row, 'custom_packagemap.0'));
            } else {
              setRuleDetail(row);
            }
            setRuleDetailVisible(true);
          }}>{get(row, indexs.rule_display_name)}</a>
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
      cell: ({ row }: any) => (<Tag className={RuleSeverityInvertEnum[get(row, indexs.rule_severity)]?.toLowerCase()}>
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
      cell: ({ row }: any) => (get(row, indexs.rule_support_language)?.join() || '通用'),
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
    if (checkable) {
      columns = concat(checkColumn, columns);
    }
    if (editable) {
      columns = concat(columns, editColumn);
    }
    if (isTmplPkgRule) {
      columns = concat(slice(columns, 0, 2), customizeColumn, slice(columns, 2));
    }
    return columns;
  };

  return (
    <>
      <RuleDetailDrawer
        visible={ruleDetailVisible}
        ruleDetail={ruleDetail}
        handleClose={() => setRuleDetailVisible(false)}
      />
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
    </>
  );
};

export default RuleTable;
