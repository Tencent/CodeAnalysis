// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 模板详情
 */
import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { get, toNumber } from 'lodash';
import { Tabs } from 'coding-oa-uikit';
import ArrowLeft from 'coding-oa-uikit/lib/icon/ArrowLeft';

import { getTmplRouter } from '@src/utils/getRoutePath';
import { getLanguages, getTags } from '@src/services/schemes';
import { getTmplInfo } from '@src/services/template';
import Loading from '@src/components/loading';

import BaseInfo from './baseinfo';
import CodeLint from './code-lint';
import CodeMetrics from './code-metrics';
import PathFilter from './path-filter';
import SchemeList from './schemes';
import Permission from './permission';

import style from './style.scss';

const { TabPane } = Tabs;

const Schemes = () => {
  const history = useHistory();
  const params: any = useParams();
  const { orgSid, teamName }: any = params;

  const [loading, setLoading] = useState(false);
  const [data, setData] = useState({}) as any;
  const [tags, setTags] = useState([]);
  const [languages, setLanguages] = useState([]);

  const tab = params.tabs || 'basic';
  const tmplId = toNumber(params.id);
  const isSysTmpl = data.scheme_key === 'public';

  useEffect(() => {
    (async () => {
      setTags(get(await getTags(orgSid), 'results', []));
      setLanguages(get(await getLanguages(), 'results', []));
    })();
  }, []);

  useEffect(() => {
    getInfo();
  }, [tmplId]);

  const getInfo = () => {
    setLoading(true);
    getTmplInfo(orgSid, tmplId)
      .then((res: any) => {
        setData(res);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <div className={style.scheme}>
      {loading ? (
        <Loading />
      ) : (
          <div className={style.container}>
            <div className={style.header}>
              <span
                className={style.backIcon}
                onClick={() => history.push(getTmplRouter(orgSid, teamName))}
              >
                <ArrowLeft />
              </span>
              <div style={{ flex: 1 }}>
                <h3 className={style.title}>{data.name}</h3>
                <p className={style.desc}>{data.description}</p>
              </div>
            </div>

            <Tabs
              activeKey={tab}
              className={style.tabs}
              onChange={(key) => {
                history.push(`${getTmplRouter(orgSid, teamName)}/${tmplId}/${key}`);
              }}
            >
              <TabPane tab="基础配置" key="basic">
                <BaseInfo
                  orgSid={orgSid}
                  isSysTmpl={isSysTmpl}
                  data={data}
                  tmplId={tmplId}
                  tags={tags}
                  languages={languages}
                  callback={data => setData(data)}
                />
              </TabPane>
              <TabPane tab="规则配置" key="codelint">
                <CodeLint
                  orgSid={orgSid}
                  teamName={teamName}
                  isSysTmpl={isSysTmpl}
                  languages={languages}
                  tmplInfo={data}
                />
              </TabPane>
              <TabPane tab="度量配置" key="codemetric">
                <CodeMetrics orgSid={orgSid} isSysTmpl={isSysTmpl} tmplId={tmplId} />
              </TabPane>
              <TabPane tab="过滤配置" key="filters">
                <PathFilter orgSid={orgSid} isSysTmpl={isSysTmpl} tmplId={tmplId} />
              </TabPane>
              {!isSysTmpl && (
                <TabPane tab="分析方案" key="schemes">
                  <SchemeList
                    teamName={teamName}
                    orgSid={orgSid}
                    tmplId={tmplId}
                  />
                </TabPane>
              )}
              {!isSysTmpl && (
                <TabPane tab="权限管理" key="permconf">
                  <Permission
                    orgSid={orgSid}
                    isSysTmpl={isSysTmpl}
                    tmplId={tmplId}
                  />
                </TabPane>
              )}
            </Tabs>
          </div>
      )}
    </div>
  );
};
export default Schemes;
