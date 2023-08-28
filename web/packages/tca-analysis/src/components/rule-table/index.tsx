import React, { useState } from 'react';
import cn from 'classnames';
import { t } from '@src/utils/i18n';
import { Space, Tag, PrimaryTableCol } from 'tdesign-react';
import { get, concat, isEmpty, slice } from 'lodash';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { RuleSeverityEnum, RuleSeverityInvertEnum, RULE_SEVERITY_CHOICES } from '@src/constant';
import RuleDetailDrawer from './rule-detail-drawer';
import s from './style.scss';

interface RuleTableProps {
  /** 团队id */
  orgSid: string;
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
  /** 自定义规则包 */
  isCustomPkg?: boolean;
  /** 是否分析方案内自定义规则 */
  isTmplPkgRule?: boolean;
  /** 选中规则的ID列表 */
  selectedRowKeys?: any;
  /** 选则规则回调函数 */
  setSelectedRowKeys?: (selectedKeys: any) => void;
  /** 编辑规则回调函数 */
  editRule?: (ruleInfo: any) => void;
  /** 移除规则回调函数 */
  removeRule?: (ruleInfo: any) => void;
  /** 获取规则详情请求 */
  getRuleDetail: (ruleId: number) => Promise<any>;
}

const RuleTable = ({
  tableData,
  orgSid,
  indexs,
  count,
  loading,
  isTmplPkgRule = false,
  isCustomPkg = false,
  editable = false,
  checkable = false,
  selectedRowKeys = null,
  getRuleDetail,
  setSelectedRowKeys = null,
  editRule = null,
  removeRule = null }: RuleTableProps) => {
  const { currentPage, pageSize } = useURLParams();
  const [ruleDetailVisible, setRuleDetailVisible] = useState<boolean>(false);
  const [ruleDetail, setRuleDetail] = useState<any>({});

  const onSelectChange = (selectedKeys: any) => {
    setSelectedRowKeys(selectedKeys);
  };

  const checkColumn: PrimaryTableCol<any> = {
    colKey: 'row-select',
    type: 'multiple',
    checkProps: ({ row }: any) => ({
      disabled: get(row, 'select_state') === 2 || get(row, 'select_state') === 1,
      checked: get(row, 'select_state') === 2 || get(row, 'select_state') === 1 || selectedRowKeys.indexOf(row?.id) !== -1,
    }),
    width: 50,
  };

  const editColumn: PrimaryTableCol<any> = {
    colKey: 'ops',
    title: t('操作'),
    width: 160,
    cell: ({ row }: any) => (
      <Space size='small'>
        <a
          onClick={() => editRule(row)}
        >
          {t('编辑')}
        </a>
        {isCustomPkg ? <a
          onClick={() => removeRule(row)}
          className={s.errorTip}
        >
          {t('移除')}
        </a> : <a
          onClick={() => removeRule(row)}
          className={cn({ [s.errorTip]: get(row, 'custom_packagemap.0.state', row.state) !== 2 })}
        >
          {get(row, 'custom_packagemap.0.state', row.state) === 2 ? t('启用') : (t('屏蔽'))}
        </a>}
      </Space>
    ),
  };

  const customizeColumn: PrimaryTableCol<any>[] = [
    {
      colKey: 'isTmplPkgRuleSeverity',
      title: t('自定义级别'),
      cell: ({ row }: any) => (!isEmpty(row?.custom_packagemap) ? <Tag className={RuleSeverityInvertEnum[get(row, 'custom_packagemap.0.severity')]?.toLowerCase()}>
        {RULE_SEVERITY_CHOICES[get(row, 'custom_packagemap.0.severity') as RuleSeverityEnum]}
      </Tag> : '- -'),
    },
  ];

  const infoColumns: PrimaryTableCol<any>[] = [
    {
      colKey: indexs.rule_display_name,
      title: t('规则名称'),
      width: 400,
      cell: ({ row }: any) => (<>
          {get(row, 'custom_packagemap.0.state', row.state) === 2 && (
            <span className={s.disabledRule}>（已屏蔽）</span>
          )}
          <a className="text-weight-bold" onClick={() => {
            if (!isEmpty(row?.custom_packagemap)) {
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
      cell: ({ row }: any) => (
        <span>
          {get(row, indexs.tool_display_name)}{get(row, 'checktool').scope === 1 && <span className='fs-12'>（私有）</span>}
        </span>),
    },
    {
      colKey: indexs.rule_severity,
      title: t('问题级别'),
      cell: ({ row }: any) => (<Tag className={RuleSeverityInvertEnum[get(row, indexs.rule_severity)]?.toLowerCase()}>
        {RULE_SEVERITY_CHOICES[get(row, indexs.rule_severity) as RuleSeverityEnum]}
      </Tag>),
    },
    {
      colKey: indexs.rule_category_name,
      title: t('分类'),
    },
    {
      colKey: indexs.rule_compile,
      title: t('是否需要编译'),
      cell: ({ row }: any) => (
          <Tag
            variant="light"
            theme={get(row, indexs.rule_compile) ? 'warning' : 'default'}
          >
            {get(row, indexs.rule_compile) ? '需要' : '无需'}编译
          </Tag>
      ),
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
    if (!isCustomPkg && isTmplPkgRule) {
      columns = concat(slice(columns, 0, 2), customizeColumn, slice(columns, 2));
    }
    return columns;
  };

  return (
    <>
      <RuleDetailDrawer
        orgSid={orgSid}
        visible={ruleDetailVisible}
        ruleDetail={ruleDetail}
        handleClose={() => setRuleDetailVisible(false)}
        getRuleDetail={getRuleDetail}
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
        tableLayout='auto'
      />
    </>
  );
};

export default RuleTable;
