// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码检查
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useHistory } from 'react-router-dom';
import { intersection, isEmpty, concat } from 'lodash';
import { Switch, message, Button, DialogPlugin, Tooltip } from 'tdesign-react';

import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import Loading from '@src/components/loading';
import { getLabels } from '@src/services/schemes';
import {
  getTmplLint,
  updateTmplLint,
  getCheckPackages,
  getAllCheckPackages,
  addCheckPackages,
  delCheckPackage,
} from '@src/services/template';
import { getTmplRouter } from '@src/utils/getRoutePath';

import { getPkgSearchFields } from '@src/constant';
import CompileConfig from '@src/components/schemes/compile-modal';
import PackageList from '@src/components/schemes/pkg-list';

import style from './style.scss';

interface CodeLintProps {
  orgSid: string;
  isSysTmpl: any;
  languages: any;
  tmplInfo: any;
  callback?: (data: any) => void;
}

const CodeLint = (props: CodeLintProps) => {
  const { orgSid, languages, tmplInfo, isSysTmpl } = props;
  const history = useHistory();
  const [selectedPkgs, setSelectedPkgs] = useState<any>([]);
  const [customPackage, setCustomPackage] = useState<any>({});
  const [data, setData] = useState<any>({});
  const [labels, setLabels] = useState([]);
  const [allPkgs, setAllPkgs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useState<any>({});
  const [firstSort, setFirstSort] = useState(true);
  const { lang = [], label = [] } = searchParams;
  const [visible, setVisible] = useState(false);

  const filterFields = getPkgSearchFields(languages, labels);

  const tmplId = tmplInfo.id;
  const checkprofile = data.checkprofile || {};

  useEffect(() => {
    (async () => {
      const labels = await getLabels();
      setLabels(labels.results || []);

      if (tmplId) {
        setLoading(true);
        setData(await getTmplLint(orgSid, tmplId));
        let pkgs = await getAllCheckPackages(orgSid, tmplId);
        pkgs = (pkgs || []).filter((item: any) => !item.disable);

        setLoading(false);
        setAllPkgs(pkgs);
      }
    })();

    setSearchParams({});
  }, [orgSid, tmplId]);

  useEffect(() => {
    if (checkprofile.id) {
      setLoading(true);
      getCheckPackages(orgSid, tmplId, {
        limit: 100,
        offset: 0,
      })
        .then((res: any) => {
          res = res.results || [];
          const ids = res.map((item: any) => item.id);
          setSelectedPkgs(ids);

          let lang = res.reduce((acc: any, item: any) => [...acc, ...item.languages], []);
          if (isEmpty(lang)) {
            lang = tmplInfo.languages || [];
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
  }, [orgSid, tmplId, tmplInfo.languages, checkprofile.id, checkprofile.custom_checkpackage]);

  const onChangeEnabled = (checked: boolean) => {
    updateConfig({ enabled: checked }).then(() => {
      message.success(`已${checked ? '开启' : '关闭'}代码检查`);
      const infoDialog = DialogPlugin({
        header: '提示',
        body: `${checked ? '开启' : '关闭'}成功，若需将改动同步到对应的分析方案请点击同步按钮`,
        theme: 'info',
        cancelBtn: null,
        onConfirm: () => {
          infoDialog.hide();
        },
      });
    });
  };

  const updateConfig = (params: any) => updateTmplLint(orgSid, tmplId, {
    ...data,
    ...params,
  }).then((res: any) => {
    setData(res);
  });

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

  const filter = (allValues: any, filterValues: any) => {
    if (isEmpty(filterValues)) return true;
    return !isEmpty(intersection(allValues, filterValues));
  };

  const handleUpdatePkg = (pkgs: any[], isAdd: boolean) => {
    setSelectedPkgs(pkgs);
    sortPkgs(pkgs, allPkgs);
    const infoDialog = DialogPlugin({
      header: '提示',
      body: `${isAdd ? '开启' : '关闭'}成功，若需将改动同步到对应的分析方案请点击同步按钮`,
      theme: 'info',
      cancelBtn: null,
      onConfirm: () => {
        infoDialog.hide();
      },
    });
  };

  const updatePkg = (isAdd: boolean, id: number) => {
    if (isAdd) {
      addCheckPackages(orgSid, tmplId, [id]).then(() => {
        const pkgs = [...selectedPkgs, id];
        handleUpdatePkg(pkgs, isAdd);
      });
    } else {
      delCheckPackage(orgSid, tmplId, id).then(() => {
        const pkgs = selectedPkgs.filter((item: any) => item !== id);
        handleUpdatePkg(pkgs, isAdd);
      });
    }
  };

  if (loading) {
    return <Loading size='small' />;
  }

  return (
    <div className={style.codeLint}>
      <div className={style.switch}>
        <span className={style.label}>是否启用</span>
        <Switch
          disabled={isSysTmpl}
          size="small"
          value={data.enabled}
          onChange={onChangeEnabled}
        />
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
            extraContent={
              !isSysTmpl && (
                <div>
                  <Button
                    style={{ marginRight: 10 }}
                    onClick={() => {
                      history.push(`${getTmplRouter(orgSid)}/${tmplId}/check-profiles/${checkprofile.id}/pkg/${customPackage.id
                      }/add-rule`);
                    }}
                    variant="outline"
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
                        history.push(`${getTmplRouter(orgSid)}/${tmplId}/check-profiles/${checkprofile.id}/checkrules`);
                      }}
                    >
                      查看已配置规则
                    </Button>
                  </Tooltip>
                  <Button onClick={() => setVisible(true)} variant="outline">编译配置</Button>
                </div>
              )
            }
          />
          <PackageList
            readonly={isSysTmpl}
            pkgs={allPkgs
              .filter((item: any) => (filter(item.labels, label) && filter(item.languages, lang))
              || selectedPkgs.includes(item.id))}
            selectedPkgs={selectedPkgs}
            customPackage={customPackage}
            updatePkg={updatePkg}
            getDetailLink={(pkgId: number) => `${getTmplRouter(orgSid)}/${tmplId}/check-profiles/${checkprofile.id}/pkg/${pkgId}`}
          />
        </>
      )}
      <CompileConfig
        visible={visible}
        data={data}
        onOk={(params: any) => {
          updateConfig(params).then(() => {
            setVisible(false);
            message.success('配置成功，若需将改动同步到对应的分析方案请点击同步按钮');
          });
        }}
        onClose={() => setVisible(false)}
      />
    </div>
  );
};

export default CodeLint;
