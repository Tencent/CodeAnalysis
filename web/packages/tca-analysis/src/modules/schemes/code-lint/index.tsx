// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码检查
 */
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useHistory } from 'react-router-dom';
import { intersection, isEmpty, concat } from 'lodash';

import { Switch, message, Tooltip, Button } from 'tdesign-react';

import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import Loading from '@src/components/loading';
import {
  updateLintConfig,
  getCheckPackages,
  getLabels,
  getAllCheckPackages,
  addCheckPackages,
  delCheckPackage,
} from '@src/services/schemes';
import { getSchemeRouter } from '@src/utils/getRoutePath';

import { getPkgSearchFields } from '@src/constant';
import CompileConfig from '@src/components/schemes/compile-modal';
import PackageList from '@src/components/schemes/pkg-list';

import style from './style.scss';

interface CodeLintProps {
  orgSid: string;
  teamName: string;
  repoId: string | number;
  schemeId: string | number;
  languages: any;
  schemeInfo: any;
  data: any;
  callback?: (data: any) => void;
}

const CodeLint = (props: CodeLintProps) => {
  const { orgSid, teamName, repoId, schemeId, languages, schemeInfo, data, callback } = props;
  const history = useHistory();

  const [visible, setVisible] = useState(false);
  const [selectedPkgs, setSelectedPkgs] = useState<any>([]);
  const [customPackage, setCustomPackage] = useState<any>({});
  const [labels, setLabels] = useState([]);
  const [allPkgs, setAllPkgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useState<any>({});
  const [firstSort, setFirstSort] = useState(true);
  const { lang = [], label = [] } = searchParams;

  const filterFields = getPkgSearchFields(languages, labels);

  const checkprofile = data.checkprofile || {};

  useEffect(() => {
    setSearchParams({});
    (async () => {
      const res = await getLabels();
      setLabels(res.results || []);

      setLoading(true);
      let pkgs = await getAllCheckPackages(orgSid, teamName, repoId, schemeId);
      pkgs = (pkgs || []).filter((item: any) => !item.disable);
      setLoading(false);
      setAllPkgs(pkgs);
    })();
  }, [orgSid, teamName, repoId, schemeId]);

  useEffect(() => {
    if (checkprofile.id) {
      setLoading(true);
      getCheckPackages(orgSid, teamName, repoId, schemeId, {
        limit: 100,
        offset: 0,
      })
        .then((res: any) => {
          res = res.results || [];
          const ids = res.map((item: any) => item.id);
          setSelectedPkgs(ids);

          let lang = res.reduce((acc: any, item: any) => [...acc, ...item.languages], []);
          if (isEmpty(lang)) {
            lang = schemeInfo.languages || [];
          }
          setSearchParams((prevState: any) => ({
            ...prevState,
            lang: [...new Set(lang)],
          }));
        })
        .finally(() => {
          setLoading(false);
        });
    }

    (async () => {
      if (checkprofile.custom_checkpackage) {
        setCustomPackage(checkprofile.custom_checkpackage);
      }
    })();
  }, [
    orgSid,
    teamName,
    repoId,
    schemeId,
    checkprofile.id,
    checkprofile.custom_checkpackage,
    schemeInfo.languages,
  ]);

  const sortPkgs = useCallback((sPkgs = selectedPkgs, aPkgs = allPkgs) => {
    setAllPkgs(concat(
      aPkgs.filter((item: any) => sPkgs.includes(item.id)),
      aPkgs.filter((item: any) => !sPkgs.includes(item.id)),
    ));
  }, [allPkgs, selectedPkgs]);

  useEffect(() => {
    if (firstSort && !isEmpty(selectedPkgs) && !isEmpty(allPkgs)) {
      sortPkgs();
      setFirstSort(false);
    }
  }, [firstSort, selectedPkgs, allPkgs, sortPkgs]);

  const onChangeEnabled = (checked: boolean) => {
    updateConfig({ enabled: checked }).then(() => {
      message.success(`已${checked ? '开启' : '关闭'}代码检查`);
    });
  };

  const updateConfig = (params: any) => updateLintConfig(orgSid, teamName, repoId, schemeId, {
    ...data,
    ...params,
  }).then((res) => {
    callback(res);
  });

  const filter = (allValues: any, filterValues: any) => {
    if (isEmpty(filterValues)) return true;
    return !isEmpty(intersection(allValues, filterValues));
  };

  const filteredPkgs = useMemo(() => (allPkgs
    .filter((item: any) => (filter(item.labels, label) && filter(item.languages, lang))
      || selectedPkgs.includes(item.id))), [allPkgs, label, lang, selectedPkgs]);

  const updatePkg = async (isAdd: boolean, id: number) => {
    let pkgs: any[] = [];

    if (isAdd) {
      await addCheckPackages(orgSid, teamName, repoId, schemeId, [id]);
      pkgs = [...selectedPkgs, id];
    } else {
      await delCheckPackage(orgSid, teamName, repoId, schemeId, id);
      pkgs = selectedPkgs.filter((item: any) => item !== id);
    }
    setSelectedPkgs(pkgs);
    sortPkgs(pkgs, allPkgs);
    message.success(`${isAdd ? '开启' : '关闭'}成功`);
  };

  if (loading) {
    return <Loading size='small' />;
  }

  return (
    <div className={style.codeLint}>
      <div className={style.switch}>
        <span className={style.label}>是否启用</span>
        <Switch size="small" value={data.enabled} onChange={onChangeEnabled} />
      </div>

      {data.enabled && (
        <>
          <Search
            fields={filterFields}
            searchParams={searchParams}
            loading={false}
            route={false}
            callback={(params: any) => {
              setSearchParams({
                ...searchParams,
                ...params,
              });
            }}
            extraContent={<div>
              <Button
                style={{ marginRight: 10 }}
                variant="outline"
                onClick={() => {
                  history.push(`${getSchemeRouter(
                    orgSid,
                    teamName,
                    repoId,
                    schemeId,
                  )}/check-profiles/${checkprofile.id}/pkg/${customPackage.id
                  }/add-rule`);
                }}
              >
                添加规则
              </Button>
              <Tooltip
                content='自定义规则包 + 官方规则包去重后的规则列表'
                overlayStyle={{ maxWidth: '350px' }}
              >
                <Button
                  style={{ marginRight: 10 }}
                  variant="outline"
                  onClick={() => {
                    history.push(`${getSchemeRouter(
                      orgSid,
                      teamName,
                      repoId,
                      schemeId,
                    )}/check-profiles/${checkprofile.id}/checkrules`);
                  }}
                >
                  查看已配置规则
                </Button>
              </Tooltip>
              <Button variant="outline" onClick={() => setVisible(true)}>编译配置</Button>
            </div>}
          />
          <PackageList
            pkgs={filteredPkgs}
            selectedPkgs={selectedPkgs}
            customPackage={customPackage}
            updatePkg={(isAdd, id) => {
              updatePkg(isAdd, id);
            }}
            getDetailLink={(pkgId: number) => (`${getSchemeRouter(
              orgSid,
              teamName,
              repoId,
              schemeId,
            )}/check-profiles/${checkprofile.id}/pkg/${pkgId}`)}
          />
        </>
      )}
      <CompileConfig
        visible={visible}
        data={data}
        onOk={(params: any) => {
          updateConfig(params).then(() => {
            setVisible(false);
            message.success('配置成功');
          });
        }}
        onClose={() => setVisible(false)}
      />
    </div>
  );
};

export default CodeLint;
