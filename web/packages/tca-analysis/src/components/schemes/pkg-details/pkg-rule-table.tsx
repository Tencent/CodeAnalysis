// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表
 */
import React, { useState } from 'react';
import { useRequest } from 'ahooks';
import { useParams, useHistory, useLocation } from 'react-router-dom';
import { toNumber, isEmpty, get } from 'lodash';
import { Button, Dialog, DialogPlugin, message, Radio } from 'tdesign-react';

import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import { useURLParams } from '@tencent/micro-frontend-shared/hooks';
import Header from '@src/components/header';
import { SEVERITY, getPkgRuleSearchFields, PKG_RULE_COLUMN_INDEX } from '@src/constant';
import RuleTable from '@src/components/rule-table';

import EditRuleModal from '@src/components/schemes/pkg-details/edit-rule-modal';
import style from './style.scss';

const getFilterOptions = (data: any) => data.map((item: any) => ({
  value: item.value,
  label: `${item.display_name}(${item.count})`,
}));

const getPageHeaderInfo = (isAllRule: boolean, isCustomPkg: boolean, pkgDetail: any) => {
  if (isAllRule) {
    return {
      title: '已配置规则列表',
      description: '自定义规则包 + 官方规则包去重后的规则列表',
    };
  }
  if (isCustomPkg) {
    return {
      title: '自定义规则包',
      description: '自定义规则包中规则配置会默认覆盖其他官方包中相同规则的配置',
    };
  }
  return {
    title: pkgDetail.name,
    description: pkgDetail.description,
  };
};

interface PkgRulesTableProps {
  isAllRule?: boolean;
  isSysTmpl?: boolean;
  getRuleDetail: (ruleId: number) => Promise<any>;
  pkgDetail?: any;
  filters: any;
  refreshDeps: any[];
  getPackagesRule: (filter: any) => Promise<any>;
  modifyRuleState: (editInfo: any) => Promise<any>;
  modifyRuleSeverity: (editInfo: any) => Promise<any>;
  delRule: (delinfo: any) => Promise<any>;
  modifyRule: (editInfo: any) => Promise<any>;
  backLink: string;
}

const PkgRulesTable = ({
  isAllRule = false,
  isSysTmpl = false,
  getRuleDetail,
  pkgDetail = {},
  filters,
  refreshDeps,
  getPackagesRule,
  modifyRule,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  backLink,
}: PkgRulesTableProps) => {
  const {
    orgSid,
  } = useParams() as any;
  const history = useHistory();
  const location = useLocation();

  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [batchModalVsb, setBatchModalVsb] = useState(false);
  const [severity, setSeverity] = useState();
  const [editRule, setEditRule] = useState({ data: {}, visible: false });

  const {
    checkrule_category: category = [],
    checkrule_language: language = [],
    severity: filterSeverity = [],
    checktool = [],
  } = filters as any;

  const filterFields = getPkgRuleSearchFields(
    filterSeverity,
    category,
    checktool,
    language,
    getFilterOptions,
  );

  const { filter, searchParams } = useURLParams(filterFields);

  const { data = {}, loading, run: refreshData } = useRequest(() => getPackagesRule(filter), {
    refreshDeps: [...refreshDeps, filter],
    onSuccess: () => {
      setSelectedRowKeys([]);
    },
  });

  const isCustomPkg = pkgDetail.package_type === 1;

  const ruleStateHandle = (state: number, keys?: any) => {
    const text = state === 2 ? '屏蔽' : '启用';
    keys = keys || selectedRowKeys;

    const confirmDialog = DialogPlugin.confirm({
      header: `${text}规则`,
      body: `您正在${text} ${
        keys.length
      } 条规则，${text}后， 在代码分析过程中将${
        state === 2 ? '忽略' : '启用'
      }这些规则，确定${text}？`,
      onConfirm: () => {
        modifyRuleState({
          packagemaps: keys,
          state,
        }).then(() => {
          message.success('规则状态修改成功');
          refreshData();
          confirmDialog.hide();
        });
      },
      onClose: () => {
        confirmDialog.hide();
      },
    });
  };

  const ruleSeverityHandle = () => {
    modifyRuleSeverity({
      packagemaps: selectedRowKeys,
      severity: toNumber(severity),
    }).then(() => {
      message.success('规则严重级别修改成功');
      refreshData();
      setBatchModalVsb(false);
    });
  };

  const delRules = (keys?: any) => {
    keys = keys || selectedRowKeys;
    const confirmDialog = DialogPlugin.confirm({
      header: '移除规则',
      body: (<>
        {isAllRule && <p style={{ color: '#3d98ff' }}>Tips: 仅会移除自定义规则包中的规则，如果为官方规则包规则则会忽略该操作</p>}
        <p>
          您正在移除 {keys.length} 个规则，移除后， 如果官方规则包存在该规则，则会采用官方包规则配置；
          如果不存在，则这些规则发现的问题将会在下次全量分析后被关闭。 所有使用当前分析方案的项目都将被影响，请慎重操作！
        </p>
      </>),
      onConfirm: () => {
        delRule({
          packagemaps: keys,
          reason: '用户移除',
        }).then(() => {
          message.success('移除规则成功');
          refreshData();
          confirmDialog.hide();
        });
      },
      onClose: () => {
        confirmDialog.hide();
      },
    });
  };

  const onRemoveRules = (ruleInfo: any) => {
    setSelectedRowKeys([ruleInfo.id]);
    if (isCustomPkg) {
      delRules([ruleInfo.id]);
    } else {
      ruleStateHandle(get(ruleInfo, 'custom_packagemap.0.state', ruleInfo.state) === 2 ? 1 : 2, [ruleInfo.id]);
    }
  };

  const onEditRule = (editRuleInfo: any) => {
    modifyRule(editRuleInfo).then(() => {
      message.success('修改规则成功');
      refreshData();
      setEditRule({ visible: false, data: {} });
    });
  };

  return (
    <div className={style.packageRules}>
      <Header
        link={backLink}
        {...getPageHeaderInfo(isAllRule, isCustomPkg, pkgDetail)}
        extraContent={isCustomPkg && !isSysTmpl && (
          <Button
            theme="primary"
            onClick={() => history.push(`${location.pathname}/add-rule`)}
          >
            添加规则
          </Button>
        )}
      />
      <Search
        fields={filterFields}
        searchParams={searchParams}
        className={style.search}
      />
      <div className={style.rules}>
        {!isEmpty(selectedRowKeys) && !isSysTmpl && (
          <div className={style.operation}>
            <Button
              variant="text"
              theme='primary'
              onClick={() => {
                setBatchModalVsb(true);
              }}
              style={{ marginRight: 10 }}
            >
              修改严重级别
            </Button>
            {(!isCustomPkg || isAllRule) && (
              <>
              <Button
                variant="text"
                theme='primary'
                onClick={() => ruleStateHandle(1)}
              >
                启用规则
              </Button>
              <Button
                variant="text"
                theme='danger'
                style={{ marginRight: 10 }}
                onClick={() => ruleStateHandle(2)}
              >
                屏蔽规则
              </Button>
            </>
            )}
            {(isCustomPkg || isAllRule) && (<Button
              variant="text"
              theme='danger'
              style={{ marginRight: 10 }}
              onClick={() => delRules()}
            >
              移除规则
            </Button>)}
          </div>
        )}
        <RuleTable
          orgSid={orgSid}
          tableData={data?.results || []}
          indexs={PKG_RULE_COLUMN_INDEX}
          count={data?.count || 0}
          loading={loading}
          checkable={!isSysTmpl}
          selectedRowKeys={selectedRowKeys}
          setSelectedRowKeys={setSelectedRowKeys}
          editable={!isSysTmpl}
          editRule={(ruleInfo: any) => setEditRule({
            data: ruleInfo,
            visible: true,
          })}
          removeRule={onRemoveRules}
          isCustomPkg={isCustomPkg}
          isTmplPkgRule
          getRuleDetail={(ruleId: number) => getRuleDetail(ruleId)}
        />
      </div>
      <Dialog
        visible={batchModalVsb}
        header="修改严重级别"
        onCancel={() => setBatchModalVsb(false)}
        onConfirm={ruleSeverityHandle}
      >
        <p style={{ marginBottom: 10 }}>
          已选定 {selectedRowKeys.length} 个规则，将其严重级别统一修改为：
        </p>
        <Radio.Group onChange={value => setSeverity(value)}>
          {Object.keys(SEVERITY).map((key: any) => (
            <Radio value={key} key={key}>
              {SEVERITY[key]}
            </Radio>
          ))}
        </Radio.Group>
      </Dialog>
      <EditRuleModal
        visible={editRule.visible}
        data={editRule.data}
        onCancel={() => setEditRule({ visible: false, data: {} })}
        onEditRule={onEditRule}
      />
    </div>
  );
};

export default PkgRulesTable;
