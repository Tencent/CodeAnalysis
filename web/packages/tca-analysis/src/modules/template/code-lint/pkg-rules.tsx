// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则列表
 */
import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import qs from 'qs';
import { useParams, useHistory, useLocation } from 'react-router-dom';
import { toNumber, isEmpty, get, omit, omitBy, cloneDeep } from 'lodash';

import { Table, Button, Modal, message, Radio, Tooltip } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import { getTmplRouter } from '@src/utils/getRoutePath';
import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/constant';
import {
  getTmplInfo,
  getPackagesRule,
  getCheckPackagesDetail,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  getRuleDetail,
  getRulesFilter,
} from '@src/services/template';
import { SEVERITY } from '../../schemes/constants';

import RuleDetail from '../../projects/issues/rule-detail';
import EditRuleModal from './edit-rule-modal';
import Search from './search';

import style from './style.scss';

const { Column } = Table;

const PkgRules = () => {
  const {
    orgSid,
    teamName,
    id: tmplId,
  } = useParams() as any;
  let { checkProfileId, pkgId } = useParams() as any;
  const history = useHistory();
  const location = useLocation();

  const [isSysTmpl, setIsSysTmpl] = useState(true);
  const [list, setList] = useState([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);
  const [pkgDetail, setPkgDetail] = useState<any>({});
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [batchModalVsb, setBatchModalVsb] = useState(false);
  const [severity, setSeverity] = useState();
  const [ruleDetailVsb, setRuleDetailVsb] = useState(false);
  const [ruleDetail, setRuleDetail] = useState({});
  const [editRule, setEditRule] = useState({ data: {}, visible: false });

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;

  const searchParams: any = omit(query, ['offset', 'limit']);

  checkProfileId = toNumber(checkProfileId);
  pkgId = toNumber(pkgId);
  const isCustomPkg = pkgDetail.package_type === 1;

  useEffect(() => {
    getTmplInfo(orgSid, tmplId).then((res: any) => {
      setIsSysTmpl(res.scheme_key === 'public');
    });
  }, [tmplId]);

  useEffect(() => {
    getPkgDetail();
    getListData();
    getPkgFilter();
  }, [pkgId]);

  const getPkgDetail = async () => {
    const res = await getCheckPackagesDetail(orgSid, tmplId, pkgId);
    setPkgDetail(res);
  };

  const getPkgFilter = async () => {
    const res = await getRulesFilter(orgSid, tmplId, pkgId);
    setFilters(res);
  };

  const getListData = (
    offset = pageStart,
    limit = pageSize,
    otherParams = searchParams,
  ) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };
    setLoading(true);
    getPackagesRule(orgSid, tmplId, pkgId, params)
      .then((res: any) => {
        let list = res.results || [];
        history.push(`${location.pathname}?${qs.stringify(params)}`);

        // 删除最后一页处理
        if (isEmpty(list) && pageStart >= pageSize && res.count > 0) {
          getListData(pageStart - pageSize, pageSize);
          return;
        }

        list = list.map((item: any) => {
          // 规则自定义处理
          if (!isEmpty(item.custom_packagemap)) {
            const rule = item.custom_packagemap[0] || {};
            item.state = rule.state;
            item.severity = rule.severity;
            item.rule_params = rule.rule_params;
          }
          return item;
        });
        setSelectedRowKeys([]);
        setCount(res.count);
        setList(list);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  const ruleStateHandle = (state: number, keys?: any) => {
    const text = state === 2 ? '屏蔽' : '启用';
    keys = keys || selectedRowKeys;

    Modal.confirm({
      title: `${text}规则`,
      content: `您正在${text} ${
        keys.length
      } 条规则，${text}后， 在代码分析过程中将${
        state === 2 ? '忽略' : '启用'
      }这些规则，确定${text}？`,
      onOk: () => {
        modifyRuleState(orgSid, tmplId, {
          packagemaps: keys,
          state,
        }).then(() => {
          message.success('规则状态修改成功');
          getListData(pageStart, pageSize);
        });
      },
    });
  };

  const ruleSeverityHandle = () => {
    modifyRuleSeverity(orgSid, tmplId, {
      packagemaps: selectedRowKeys,
      severity: toNumber(severity),
    }).then(() => {
      message.success('规则严重级别修改成功');
      getListData(pageStart, pageSize);
      setBatchModalVsb(false);
    });
  };

  const delRules = (keys?: any) => {
    keys = keys || selectedRowKeys;
    Modal.confirm({
      title: '移除规则',
      content: `您正在移除 ${keys.length} 个规则，移除后， 如果官方规则包存在该规则，则会采用官方包规则配置；如果不存在，则这些规则发现的问题将会在下次全量分析后被关闭。 所有使用当前分析方案的项目都将被影响，请慎重操作！`,
      onOk: () => {
        delRule(orgSid, tmplId, {
          packagemaps: keys,
          reason: '用户移除',
        }).then(() => {
          message.success('移除规则成功');
          getListData(pageStart, pageSize);
        });
      },
      onCancel: () => {
        setSelectedRowKeys([]);
      },
    });
  };

  const openRuleDetail = async (ruleId: number) => {
    setRuleDetailVsb(true);
    const res = await getRuleDetail(orgSid, tmplId, ruleId);
    setRuleDetail(res);
  };

  return (
    <div className={style.packageRules}>
      <div className={style.header}>
        <span
          className={style.backIcon}
          onClick={() => history.push(`${getTmplRouter(orgSid, teamName)}/${tmplId}/codelint`)
          }
        >
          <ArrowLeft />
        </span>
        <div style={{ flex: 1 }}>
          <h3 className={style.title}>
            {isCustomPkg ? '自定义规则包' : pkgDetail.name}
          </h3>
          <p className={style.desc}>
            {isCustomPkg
              ? '自定义规则包中规则配置会默认覆盖其他官方包中相同规则的配置'
              : pkgDetail.description}
          </p>
        </div>
        {isCustomPkg && !isSysTmpl && (
          <Button
            type="primary"
            onClick={() => history.push(`${location.pathname}/add-rule`)}
          >
            添加规则
          </Button>
        )}
      </div>

      <Search
        loading={loading}
        searchParams={cloneDeep(searchParams)}
        filters={filters}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      <div className={style.rules}>
        {!isEmpty(selectedRowKeys) && !isSysTmpl && (
          <div className={style.operation}>
            <Button
              type="link"
              onClick={() => {
                setBatchModalVsb(true);
              }}
              style={{ marginRight: 10 }}
            >
              修改严重级别
            </Button>
            {isCustomPkg ? (
              <Button
                type="link"
                style={{ marginRight: 10 }}
                onClick={() => delRules()}
              >
                移除规则
              </Button>
            ) : (
              <>
                <Button
                  type="link"
                  style={{ marginRight: 10 }}
                  onClick={() => ruleStateHandle(2)}
                >
                  屏蔽规则
                </Button>
                <Button type="link" onClick={() => ruleStateHandle(1)}>
                  启用规则
                </Button>
              </>
            )}
          </div>
        )}
        <Table
          dataSource={list}
          className={style.ruleTable}
          scroll={{ x: 1500 }}
          loading={loading}
          rowKey={(item: any) => item.id}
          rowSelection={
            !isSysTmpl
              ? {
                selectedRowKeys,
                onChange: keys => setSelectedRowKeys(keys),
              }
              : undefined
          }
          pagination={{
            current: Math.floor(pageStart / pageSize) + 1,
            total: count,
            pageSize,
            showSizeChanger: true,
            showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
            onChange: onChangePageSize,
            onShowSizeChange,
          }}
        >
          <Column
            title="规则名称"
            width="12%"
            dataIndex={['checkrule', 'real_name']}
            render={(name, data: any) => (
              <p
                className={style.ruleName}
                onClick={() => {
                  openRuleDetail(get(data, 'checkrule.id'));
                }}
              >
                {data.state === 2 && (
                  <span className={style.disabledRule}>（已屏蔽）</span>
                )}
                {name}
              </p>
            )}
          />
          <Column
            title="规则概要"
            width="36%"
            dataIndex={['checkrule', 'rule_title']}
          />
          <Column title="所属工具" dataIndex={['checktool', 'display_name']} />
          <Column
            title="规则参数"
            dataIndex={['checkrule', 'rule_params']}
            render={(params, data: any) => {
              const value = data.rule_params || params;
              return value && value.length > 30 ? (
                <Tooltip title={value} overlayStyle={{ maxWidth: 350 }}>
                  <p className={style.ruleDesc}>{value}</p>
                </Tooltip>
              ) : (
                value
              );
            }}
          />
          <Column
            title="分类"
            width={100}
            dataIndex={['checkrule', 'category_name']}
          />
          <Column
            title="问题级别"
            width={80}
            dataIndex={['checkrule', 'severity_name']}
            render={(severity, data: any) => SEVERITY[data.severity || severity]
            }
          />
          {!isSysTmpl && (
            <Column
              title="操作"
              dataIndex="id"
              width={100}
              render={(id, item: any) => (
                <>
                  <a
                    style={{ marginRight: 10 }}
                    onClick={() => {
                      setEditRule({
                        data: item,
                        visible: true,
                      });
                    }}
                  >
                    编辑
                  </a>
                  {isCustomPkg ? (
                    <a
                      className={style.errorTip}
                      onClick={() => {
                        setSelectedRowKeys([id]);
                        delRules([id]);
                      }}
                    >
                      移除
                    </a>
                  ) : (
                    <a
                      className={cn({ [style.errorTip]: item.state === 1 })}
                      onClick={() => {
                        setSelectedRowKeys([id]);
                        ruleStateHandle(item.state === 2 ? 1 : 2, [id]);
                      }}
                    >
                      {item.state === 2 ? '取消屏蔽' : '屏蔽'}
                    </a>
                  )}
                </>
              )}
            />
          )}
        </Table>
      </div>
      <Modal
        visible={batchModalVsb}
        title="修改严重级别"
        onCancel={() => setBatchModalVsb(false)}
        onOk={ruleSeverityHandle}
      >
        <p style={{ marginBottom: 10 }}>
          已选定 {selectedRowKeys.length} 个规则，将其严重级别统一修改为：
        </p>
        <Radio.Group onChange={e => setSeverity(e.target.value)}>
          {Object.keys(SEVERITY).map((key: any) => (
            <Radio value={key} key={key}>
              {SEVERITY[key]}
            </Radio>
          ))}
        </Radio.Group>
      </Modal>
      <RuleDetail
        visible={ruleDetailVsb}
        onClose={() => setRuleDetailVsb(false)}
        data={ruleDetail}
      />
      <EditRuleModal
        orgSid={orgSid}
        tmplId={tmplId}
        checkProfileId={checkProfileId}
        visible={editRule.visible}
        data={editRule.data}
        onCancel={() => setEditRule({ visible: false, data: {} })}
        callback={() => getListData(pageStart, pageSize)}
      />
    </div>
  );
};

export default PkgRules;
