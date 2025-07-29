// Copyright (c) 2021-2025 Tencent
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案入口文件
 */
import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import cn from 'classnames';
import { get, findIndex, isEmpty, toNumber, find } from 'lodash';
import { Tabs, Button } from 'tdesign-react';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';

import { useStateStore } from '@src/context/store';
import Repos from '@src/components/repos';
import { getSchemeRouter, getTmplBlankRouter } from '@src/utils/getRoutePath';
import { getSchemes, getLanguages, getTags, getSchemeBasic, getLintConfig } from '@src/services/schemes';
import { getTmplList } from '@src/services/template';
import noDataSvg from '@src/images/no-data.svg';
import Loading from '@src/components/loading';

import List from './list';
import CreateSchemeModal from './create-scheme';
import BaseInfo from './baseinfo';
import CodeLint from './code-lint';
import CodeMetrics from './code-metrics';
import PathFilter from './path-filter';
import Branchs from './branchs';
import PullModal from './pull-tmpl-modal';

import style from './style.scss';

const { TabPanel } = Tabs;

const Schemes = () => {
  const history = useHistory();
  const params: any = useParams();

  const { curRepo } = useStateStore();
  const [schemes, setSchemes] = useState([]);
  const [schemesLoading, setSchemesLoading] = useState(false);
  const [schemeInfo, setSchemeInfo] = useState({}) as any;
  const [visible, setVisible] = useState(false);
  const [tags, setTags] = useState([]);
  const [languages, setLanguages] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [lintConfig, setLintConfig] = useState<any>({});
  const [pullModalVsb, setPullModalVsb] = useState(false);

  const tab = params.tabs || 'basic';
  const schemeId = toNumber(params.schemeId);
  const repoId = toNumber(params.repoId) || curRepo.id;
  const { orgSid, teamName } = params;

  useEffect(() => {
    getCommonData();
  }, []);

  useEffect(() => {
    schemeId && getLintConf();
  }, [schemeId]);

  useEffect(() => {
    if (repoId) {
      history.replace(`${getSchemeRouter(orgSid, teamName, repoId, schemeId)}`);

      (async () => {
        getSchemeList(schemeId);
      })();
    }
  }, [repoId]);

  const getCommonData = async () => {
    setTags(get(await getTags(orgSid), 'results', []));
    setLanguages(get(await getLanguages(), 'results', []));
    setTemplates(get(await getTmplList(orgSid, { limit: 100 }), 'results', []));
  };

  const getLintConf = async () => {
    setLintConfig(await getLintConfig(orgSid, teamName, repoId, schemeId));
  };

  const getSchemeList = async (schemeId?: string | number) => {
    setSchemesLoading(true);
    let res = await getSchemes(orgSid, teamName, repoId, { limit: 1000 });
    res = res.results || [];
    setSchemes(res);
    setSchemesLoading(false);

    const defaultScheme = find(res, { default_flag: true, status: 1 }) || {};

    const id = schemeId || defaultScheme.id || get(res, '[0].id');
    getSchemeInfo(id);
  };

  const getSchemeInfo = async (schemeId: string | number) => {
    if (schemeId) {
      const res = await getSchemeBasic(orgSid, teamName, repoId, schemeId);
      setSchemeInfo(res);
      history.replace(`${getSchemeRouter(orgSid, teamName, repoId, schemeId)}/${tab}`);
    }
  };

  return (
    <div className={style.scheme}>
      <Repos
        orgSid={orgSid}
        teamName={teamName}
        callback={(repo: any) => history.push(getSchemeRouter(orgSid, teamName, repo.id))}
      />
      {/* eslint-disable-next-line */}
      {schemesLoading ? (
        <Loading />
      ) : isEmpty(schemes) ? (
        <div className={style.noData}>
          <img src={noDataSvg} />
          <div>暂无方案</div>
          <Button icon={<PlusIcon />} onClick={() => setVisible(true)}>
            新建分析方案
          </Button>
        </div>
      ) : (
        <div className={style.schemeContainer}>
          <List
            repoId={repoId}
            scheme={schemeInfo}
            schemeList={schemes}
            addSchemeHandle={() => {
              setVisible(true);
            }}
            changeSchemeHandle={(item) => {
              getSchemeInfo(item.id);
            }}
          />
          <div className={style.schemeRight}>
            <div style={{ marginBottom: 20 }}>
              <div className={style.header}>
                <p className={style.title}>{schemeInfo.name}</p>
                {schemeInfo.default_flag && schemeInfo.status === 1 && (
                  <span className={style.label}>Default</span>
                )}
                {schemeInfo.status === 2 && (
                  <span className={cn(style.label, style.deprecatedLabel)}>
                    已废弃
                  </span>
                )}
              </div>
              {schemeInfo.refer_scheme?.is_template && (
                <p className={style.tmplDesc}>
                  该分析方案由模板
                  <a
                    href={`${getTmplBlankRouter(orgSid)}/${schemeInfo.refer_scheme.id}`}
                    target="_blank" rel="noreferrer"
                  >
                    「{schemeInfo.refer_scheme.name}」
                  </a>
                  创建；若需同步模板配置，请点击
                  <a onClick={() => setPullModalVsb(true)}>
                    同步
                  </a>
                </p>
              )}
            </div>
            <Tabs
              value={tab}
              className={style.tabs}
              onChange={(key) => {
                history.push(`${getSchemeRouter(
                  orgSid,
                  teamName,
                  repoId,
                  schemeInfo.id,
                )}/${key}`);
              }}
              defaultValue='basic'
            >
              <TabPanel label="基础配置" value="basic">
                <BaseInfo
                  orgSid={orgSid}
                  teamName={teamName}
                  data={schemeInfo}
                  lintConf={lintConfig}
                  repoId={repoId}
                  tags={tags}
                  languages={languages}
                  callback={(data: any) => {
                    let list: any = [...schemes];
                    const index = findIndex(schemes as any, { id: data.id });
                    if (index > -1) {
                      list[index] = data;
                      if (data.default_flag) {
                        list = list.map((item: any) => (item.id === data.id
                          ? data
                          : { ...item, default_flag: false }));
                      }
                      setSchemes(list);
                      setSchemeInfo(data);
                    }
                  }}
                />
              </TabPanel>
              <TabPanel label="规则配置" value="codelint">
                <CodeLint
                  data={lintConfig}
                  orgSid={orgSid}
                  teamName={teamName}
                  repoId={repoId}
                  schemeId={schemeInfo.id}
                  languages={languages}
                  schemeInfo={schemeInfo}
                  callback={(data: any) => {
                    setLintConfig(data);
                  }}
                />
              </TabPanel>
              <TabPanel label="度量配置" value="codemetric">
                <CodeMetrics
                  orgSid={orgSid}
                  teamName={teamName}
                  repoId={repoId}
                  schemeId={schemeInfo.id}
                />
              </TabPanel>
              <TabPanel label="过滤配置" value="filters">
                <PathFilter
                  orgSid={orgSid}
                  teamName={teamName}
                  repoId={repoId}
                  schemeId={schemeInfo.id}
                />
              </TabPanel>
              <TabPanel label="已关联分支" value="branchs">
                <Branchs
                  orgSid={orgSid}
                  teamName={teamName}
                  repoId={repoId}
                  schemeId={schemeInfo.id}
                />
              </TabPanel>
            </Tabs>
          </div>
        </div>
      )}
      <CreateSchemeModal
        orgSid={orgSid}
        teamName={teamName}
        visible={visible}
        tags={tags}
        languages={languages}
        schemeList={schemes}
        repoId={repoId}
        templates={templates}
        onClose={() => {
          setVisible(false);
        }}
        callback={(id) => {
          getSchemeList(id);
        }}
      />
      <PullModal
        orgSid={orgSid}
        teamName={teamName}
        repoId={repoId}
        schemeId={schemeInfo.id}
        visible={pullModalVsb}
        onClose={() => setPullModalVsb(false)}
        callback={(id: number | string) => {
          getSchemeInfo(id);
        }}
      />
    </div>
  );
};
export default Schemes;
