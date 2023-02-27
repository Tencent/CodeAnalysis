/**
 * 已配置规则列表 - 分析方案/分析方案模板公用
 */
import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import qs from 'qs';
import { useParams, useHistory, useLocation } from 'react-router-dom';
import { toNumber, isEmpty, get, omit, omitBy, cloneDeep } from 'lodash';
import { Table, Button, Modal, Radio, Tooltip, message, Tag } from 'coding-oa-uikit';

import Header from '@src/components/header';
import { getSchemeRouter, getTmplRouter } from '@src/utils/getRoutePath';
import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/constant';
import { SEVERITY } from '../constants';
import {
  getAllCheckRules,
  getAllCheckRulesFilters,
  modifyRuleState,
  modifyRuleSeverity,
  delRule,
  getRuleDetail,
} from '@src/services/schemes';

import RuleDetail from '@src/modules/projects/issues/rule-detail';
import EditRuleModal from './edit-rule-modal';
import Search from './search';
import style from './style.scss';

const { Column } = Table;

const CheckRules = () => {
  const { orgSid, teamName, repoId, schemeId, id: tmplId } = useParams<any>();
  let { checkProfileId } = useParams<any>();

  const history = useHistory();
  const location = useLocation();

  const [list, setList] = useState([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [filters, setFilters] = useState({});
  const [loading, setLoading] = useState(false);
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

  useEffect(() => {
    getListData();

    getAllCheckRulesFilters(orgSid, teamName, repoId, schemeId).then((res: any) => {
      setFilters(res);
    });
  }, [checkProfileId]);

  const getListData = (
    offset = DEFAULT_PAGER.pageStart,
    limit = DEFAULT_PAGER.pageSize,
    otherParams = searchParams,
  ) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };
    setLoading(true);

    checkProfileId && getAllCheckRules(orgSid, teamName, repoId, schemeId, params)
      .then((res: any) => {
        let list = res.results || [];
        history.push(`${location.pathname}?${qs.stringify(params)}`);

        // 删除最后一页处理
        if (isEmpty(list) && offset >= limit && res.count > 0) {
          getListData(offset - limit, limit);
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

  const delRules = (keys?: any) => {
    keys = keys || selectedRowKeys;
    Modal.confirm({
      title: '移除规则',
      content: (
        <>
          <p style={{ color: '#3d98ff' }}>Tips: 仅会移除自定义规则包中的规则，如果为官方规则包规则则会忽略该操作</p>
          <p>
            您正在移除 {keys.length} 个规则，移除后， 如果官方规则包存在该规则，则会采用官方包规则配置；
            如果不存在，则这些规则发现的问题将会在下次全量分析后被关闭。 所有使用当前分析方案的项目都将被影响，请慎重操作！
          </p>
        </>
      ),
      onOk: () => {
        delRule(orgSid, teamName, repoId, schemeId, {
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

  const ruleStateHandle = (state: number, keys?: any) => {
    const text = state === 2 ? '屏蔽' : '启用';
    keys = keys || selectedRowKeys;

    Modal.confirm({
      title: `${text}规则`,
      content: (
        <>
          <p style={{ color: '#3d98ff' }}>
            Tips: 屏蔽规则会在下次分析时忽略该规则，对规则包内的规则进行自定义，本质是向自定义规则包增加规则
          </p>
          <p>
            您正在{text} {keys.length} 条规则，{text}后，
            在代码分析过程中将{state === 2 ? '忽略' : '启用'}这些规则，确定{text}？
          </p>
        </>
      ),
      onOk: () => {
        modifyRuleState(orgSid, teamName, repoId, schemeId, {
          packagemaps: keys,
          state,
        }).then(() => {
          message.success('规则状态修改成功');
          getListData(pageStart, pageSize);
        });
      },
    });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  const openRuleDetail = (ruleId: number) => {
    setRuleDetailVsb(true);

    getRuleDetail(orgSid, teamName, repoId, schemeId, ruleId).then((res: any) => {
      setRuleDetail(res);
    });
  };

  const ruleSeverityHandle = () => {
    modifyRuleSeverity(orgSid, teamName, repoId, schemeId, {
      packagemaps: selectedRowKeys,
      severity: toNumber(severity),
    }).then(() => {
      message.success('规则严重级别修改成功');
      getListData(pageStart, pageSize);
      setBatchModalVsb(false);
    });
  };

  return (
    <div className={style.packageRules}>
      <div className={style.flex}>
        <Header
          title='已配置规则列表'
          link={tmplId ? `${getTmplRouter(orgSid, teamName)}/${tmplId}/codelint` : `${getSchemeRouter(orgSid, teamName, repoId, schemeId)}/codelint`}
          description='自定义规则包 + 官方规则包去重后的规则列表'
        />
        <Button
          type="primary"
          onClick={() => history.push(tmplId
            ? `${getTmplRouter(orgSid, teamName)}/${tmplId}/check-profiles/${checkProfileId}/add-rule`
            : `${getSchemeRouter(orgSid, teamName, repoId, schemeId)}/check-profiles/${checkProfileId}/add-rule`)}
        >
          添加规则
        </Button>
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
        {!isEmpty(selectedRowKeys) && (
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
            <Button
              type="link"
              style={{ marginRight: 10 }}
              onClick={() => ruleStateHandle(1)}
            >
              启用规则
            </Button>
            <Button
              type="link"
              danger
              style={{ marginRight: 10 }}
              onClick={() => ruleStateHandle(2)}
            >
              屏蔽规则
            </Button>
            <Tooltip title='仅会移除自定义规则包中的规则，如果为官方规则包规则则会忽略该操作'>
              <Button
                type="link"
                danger
                onClick={() => delRules()}
              >
                移除规则
            </Button>
            </Tooltip>
          </div>
        )}
        <Table
          dataSource={list}
          className={style.ruleTable}
          scroll={{ x: 1500 }}
          loading={loading}
          rowKey={(item: any) => item.id}
          rowSelection={{
            selectedRowKeys,
            onChange: (keys: any) => setSelectedRowKeys(keys),
          }}
          pagination={{
            current: Math.floor(pageStart / pageSize) + 1,
            total: count,
            pageSize,
            showSizeChanger: true,
            showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
            onChange: onChangePageSize,
            onShowSizeChange,
          }}
        >
          <Column
            title="规则名称"
            // width="12%"
            dataIndex={['checkrule', 'display_name']}
            render={(name: any, data: any) => (
              <p
                className={style.ruleName}
                onClick={() => openRuleDetail(get(data, 'checkrule.id'))}
              >
                {name}
                {data.state === 2 && (
                  <Tooltip title='该规则被屏蔽，分析时会忽略该规则'>
                    <span style={{ color: '#fc9c9c' }}>（已屏蔽）</span>
                  </Tooltip>
                )}
                {data.is_custom && (
                  <Tooltip title='自定义规则包内的规则'>
                    <span style={{ color: '#8cc6ff' }}>（自定义）</span>
                  </Tooltip>
                )}
              </p>
            )}
          />
          <Column title="规则概要" width="36%" dataIndex={['checkrule', 'rule_title']} />
          <Column title="所属工具" dataIndex={['checktool', 'display_name']} />
          <Column
            title="规则参数"
            dataIndex={['checkrule', 'rule_params']}
            render={(params: any, data: any) => {
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
          <Column title="分类" width={100} dataIndex={['checkrule', 'category_name']} />
          <Column
            title="问题级别"
            width={80}
            dataIndex={['checkrule', 'severity_name']}
            render={(severity: any, data: any) => SEVERITY[data.severity || severity]}
          />
           <Column
            title="是否需要编译"
            width={120}
            dataIndex={['checktool', 'build_flag']}
            render={(buildFlag: boolean) => (
              <Tag
                style={{ margin: 0 }}
                className={buildFlag && style.buildTag}
              >
                {buildFlag ? '需要' : '无需'}编译
              </Tag>
            )}
          />
          <Column
            title="操作"
            dataIndex="id"
            width={120}
            render={(id: any, item: any) => (
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
                <a
                  className={cn({ [style.errorTip]: item.state === 1 })}
                  onClick={() => {
                    setSelectedRowKeys([id]);
                    ruleStateHandle(item.state === 2 ? 1 : 2, [id]);
                  }}
                >
                  {item.state === 2 ? '启用' : '屏蔽'}
                </a>
              </>
            )}
          />
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
        <Radio.Group onChange={(e: any) => setSeverity(e.target.value)}>
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
       teamName={teamName}
       repoId={repoId}
       schemeId={schemeId}
        visible={editRule.visible}
        data={editRule.data}
        onCancel={() => setEditRule({ visible: false, data: {} })}
        callback={() => getListData(pageStart, pageSize)}
      />
    </div>
  );
};


export default CheckRules;
