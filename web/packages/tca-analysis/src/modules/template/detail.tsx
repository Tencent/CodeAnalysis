// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 模板详情
 */
import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import { useHistory, useParams } from 'react-router-dom';
import { get, toNumber } from 'lodash';
import { Tabs, Loading, Button, message, Tag } from 'tdesign-react';
import Header from '@src/components/header';

import { getTmplRouter } from '@src/utils/getRoutePath';
import { getLanguages, getTags } from '@src/services/schemes';
import { getTmplInfo, syncScheme } from '@src/services/template';

import BaseInfo from './baseinfo';
import CodeLint from './code-lint';
import CodeMetrics from './code-metrics';
import PathFilter from './path-filter';
import SchemeList from './schemes';
import Permission from './permission';
import SyncModal from './sync-modal';

import style from './style.scss';

const { TabPanel } = Tabs;

const Schemes = () => {
  const history = useHistory();
  const params: any = useParams();
  const { orgSid }: any = params;

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({}) as any;
  const [tags, setTags] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [syncVsb, setSyncVsb] = useState(false);

  const tab = params.tabs || 'basic';
  const tmplId = toNumber(params.id);
  const isSysTmpl = data.scheme_key === 'public';

  useEffect(() => {
    (async () => {
      setTags(get(await getTags(orgSid), 'results', []));
      setLanguages(get(await getLanguages(), 'results', []));
    })();
  }, [orgSid]);

  useEffect(() => {
    setLoading(true);
    getTmplInfo(orgSid, tmplId)
      .then((res: any) => {
        setData(res);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [orgSid, tmplId]);

  if (loading) {
    return <div className={style.loading}><Loading size='small' /></div>;
  }

  const onSync = (keys: any) => {
    if (keys.length > 0) {
      syncScheme(orgSid, tmplId, {
        sync_lint_build_conf: true,
        sync_lint_rule_conf: true,
        schemes: keys,
      }).then(() => {
        message.success('同步成功');
        setSyncVsb(false);
      });
    } else {
      message.warning('请选择需要同步的分析方案');
    }
  };

  return (
    <div>
      <div className={style.container}>
        <Header
          link={getTmplRouter(orgSid)}
          title={<div className={style.tmplTitle}>
            {data.name}
            <Tag
              size='small'
              className={cn(style.tmplTag, { [style.sys]: data.scheme_key === 'public' })}
            >
              {data.scheme_key === 'public' ? '系统模板' : '自定义模板'}
            </Tag>
          </div>}
          description={data.description}
          extraContent={!isSysTmpl && <Button
            theme="primary"
            onClick={() => {
              setSyncVsb(true);
            }}
          >
            同步
          </Button>}
        />
        {!isSysTmpl && <SyncModal
            onlySync
            tmplId={tmplId}
            visible={syncVsb}
            onClose={() => setSyncVsb(false)}
            onOk={onSync}
          />}
        <Tabs
          value={tab}
          className={style.tabs}
          size='large'
          onChange={(key) => {
            history.push(`${getTmplRouter(orgSid)}/${tmplId}/${key}`);
          }}
        >
          <TabPanel label="基础配置" value="basic">
            <BaseInfo
              orgSid={orgSid}
              isSysTmpl={isSysTmpl}
              data={data}
              tmplId={tmplId}
              tags={tags}
              languages={languages}
              callback={data => setData(data)}
            />
          </TabPanel>
          <TabPanel label="规则配置" value="codelint">
            <CodeLint
              orgSid={orgSid}
              isSysTmpl={isSysTmpl}
              languages={languages}
              tmplInfo={data}
            />
          </TabPanel>
          <TabPanel label="度量配置" value="codemetric">
            <CodeMetrics orgSid={orgSid} isSysTmpl={isSysTmpl} tmplId={tmplId} />
          </TabPanel>
          <TabPanel label="过滤配置" value="filters">
            <PathFilter orgSid={orgSid} isSysTmpl={isSysTmpl} tmplId={tmplId} />
          </TabPanel>
          {!isSysTmpl && (
            <TabPanel label="分析方案" value="schemes">
              <SchemeList
                orgSid={orgSid}
                tmplId={tmplId}
              />
            </TabPanel>
          )}
          {!isSysTmpl && (
            <TabPanel label="权限管理" value="permconf">
              <Permission
                orgSid={orgSid}
                isSysTmpl={isSysTmpl}
                tmplId={tmplId}
              />
            </TabPanel>
          )}
        </Tabs>
      </div>
    </div>
  );
};
export default Schemes;
