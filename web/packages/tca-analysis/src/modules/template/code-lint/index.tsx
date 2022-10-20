// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码检查
 */
import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import cn from 'classnames';
import { intersection, isEmpty, concat } from 'lodash';

import { Switch, message, Tooltip, Typography, Button, Modal } from 'coding-oa-uikit';
import Items from 'coding-oa-uikit/lib/icon/Items';
import Globe from 'coding-oa-uikit/lib/icon/Globe';
import Pencil from 'coding-oa-uikit/lib/icon/Pencil';
import AngleRight from 'coding-oa-uikit/lib/icon/AngleRight';

import Loading from '@src/components/loading';

import { getLabels } from '@src/services/schemes';
import {
  getTmplLint,
  updateTmplLint,
  syncScheme,
  getCheckPackages,
  getAllCheckPackages,
  addCheckPackages,
  delCheckPackage,
} from '@src/services/template';
import { getTmplRouter, getTmplBlankRouter } from '@src/utils/getRoutePath';

import Filter from '@src/components/filter';
import SelectBorderless from '@src/components/select-borderless';
import SyncModal from '../sync-modal';
import CompileConfig from '../../schemes/code-lint/compile-modal';

import style from './style.scss';

interface CodeLintProps {
  orgSid: string;
  teamName: string;
  isSysTmpl: any;
  languages: any;
  tmplInfo: any;
  callback?: (data: any) => void;
}

const CodeLint = (props: CodeLintProps) => {
  const { orgSid, teamName, languages, tmplInfo, isSysTmpl } = props;
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
  const [syncVsb, setSyncVsb] = useState(false);

  const tmplId = tmplInfo.id;
  const checkprofile = data.checkprofile || {};

  useEffect(() => {
    (async () => {
      const labels = await getLabels();
      setLabels(labels.results || []);

      if (tmplId) {
        setLoading(true);
        let pkgs = await getAllCheckPackages(orgSid, tmplId);
        pkgs = (pkgs || []).filter((item: any) => !item.disable);

        setLoading(false);
        setAllPkgs(pkgs);
      }
    })();
  }, []);

  useEffect(() => {
    (async () => {
      tmplId && setData(await getTmplLint(orgSid, tmplId));
    })();
    setSearchParams({});
  }, [tmplId]);

  useEffect(() => {
    getList();

    (async () => {
      if (checkprofile.custom_checkpackage) {
        setCustomPackage(checkprofile.custom_checkpackage);
      }
    })();
  }, [checkprofile.id]);

  useEffect(() => {
    if (firstSort && !isEmpty(selectedPkgs) && !isEmpty(allPkgs)) {
      sortPkgs();
      setFirstSort(false);
    }
  });

  const onChangeEnabled = (checked: boolean) => {
    updateConfig({ enabled: checked }).then(() => {
      message.success(`已${checked ? '开启' : '关闭'}代码检查`);
    });
  };

  const updateConfig = (params: any) => updateTmplLint(orgSid, tmplId, {
    ...data,
    ...params,
  }).then((res) => {
    setData(res);
  });

  const getList = async () => {
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
          setSearchParams({
            ...searchParams,
            lang: [...new Set(lang)],
          });
        })
        .finally(() => {
          setLoading(false);
        });
    }
  };

  const sortPkgs = (sPkgs = selectedPkgs, aPkgs = allPkgs) => {
    setAllPkgs(concat(
      aPkgs.filter((item: any) => sPkgs.includes(item.id)),
      aPkgs.filter((item: any) => !sPkgs.includes(item.id)),
    ));
  };

  const filter = (allValues: any, filterValues: any) => {
    if (isEmpty(filterValues)) return true;
    return !isEmpty(intersection(allValues, filterValues));
  };

  const updatePkg = async (isAdd: boolean, id: number) => {
    let pkgs: any[] = [];

    if (isAdd) {
      await addCheckPackages(orgSid, tmplId, [id]);
      pkgs = [...selectedPkgs, id];
    } else {
      await delCheckPackage(orgSid, tmplId, id);
      pkgs = selectedPkgs.filter((item: any) => item !== id);
    }
    setSelectedPkgs(pkgs);
    sortPkgs(pkgs, allPkgs);
    Modal.warning({
      title: '提示',
      content: `${isAdd ? '开启' : '关闭'}成功，若需将改动同步到对应的分析方案请点击同步按钮`,
    });
    // message.success(`${isAdd ? '开启' : '关闭'}成功，若需将改动同步到对应的分析方案请点击同步按钮`, 5);
  };

  if (loading) {
    return <Loading />;
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
    <div className={style.codeLint}>
      <div className={style.switch}>
        <span className={style.label}>是否启用</span>
        <Switch
          disabled={isSysTmpl}
          size="small"
          checked={data.enabled}
          onChange={onChangeEnabled}
        />
      </div>

      {data.enabled && (
        <>
          <div className={style.search}>
            <Filter>
              <Filter.Item label="语言">
                <SelectBorderless
                  multiple
                  allowClear
                  placeholder="全部"
                  value={lang}
                  data={languages.map((item: any) => ({
                    value: item.name,
                    text: item.display_name,
                  }))}
                  onChange={(value: any) => {
                    setSearchParams({
                      ...searchParams,
                      lang: value,
                    });
                  }}
                />
              </Filter.Item>
              <Filter.Item label="分类">
                <SelectBorderless
                  multiple
                  allowClear
                  placeholder="全部"
                  value={label}
                  data={labels.map((item: any) => ({
                    value: item.name,
                    text: item.name,
                  }))}
                  onChange={(value: any) => {
                    setSearchParams({
                      ...searchParams,
                      label: value,
                    });
                  }}
                />
              </Filter.Item>
            </Filter>
            {
              !isSysTmpl && (
                <div>
                  <Button
                    style={{ marginRight: 10 }}
                    onClick={() => {
                      history.push(`${getTmplRouter(
                        orgSid,
                        teamName,
                      )}/${tmplId}/check-profiles/${checkprofile.id}/pkg/${customPackage.id
                      }/add-rule`);
                    }}
                  >
                    添加规则
                  </Button>
                  <Button onClick={() => setVisible(true)}>编译配置</Button>
                </div>
              )
            }
          </div>
          <div className={style.pkgWrapper}>
            <div className={style.package}>
              <div className={style.header}>
                <span className={style.name}>自定义规则包</span>
                <Switch checked={true} disabled />
              </div>
              <div style={{ marginBottom: 20 }}>
                <span className={style.label}>自定义</span>
              </div>
              <div className={cn(style.description, style.common)}>
                <Items className={style.icon} />
                <p>自定义规则包中规则配置会默认覆盖其他官方包中相同规则的配置</p>
              </div>
              <div className={cn(style.language, style.common)}>
                <Pencil className={style.icon} />
                <p>自定义规则 {customPackage.checkrule_count} 条</p>
              </div>
              <div className={style.footer}>
                <a
                  target="_blank"
                  href={`${getTmplBlankRouter(
                    orgSid,
                    teamName,
                  )}/${tmplId}/check-profiles/${checkprofile.id}/pkg/${customPackage.id
                  }`} rel="noreferrer"
                >
                  查看详细规则 <AngleRight />
                </a>
              </div>
            </div>

            {allPkgs
              .filter((item: any) => (filter(item.labels, label) && filter(item.languages, lang))
                || selectedPkgs.includes(item.id))
              .map((item: any) => (
                <Item
                  orgSid={orgSid}
                  teamName={teamName}
                  disabled={isSysTmpl}
                  key={item.id}
                  checked={selectedPkgs.includes(item.id)}
                  item={item}
                  tmplId={tmplId}
                  checkprofileId={checkprofile.id}
                  onChange={updatePkg}
                />
              ))}
          </div>
        </>
      )}
      {!isSysTmpl && (
        <>
          <Button
            type="primary"
            onClick={() => {
              setSyncVsb(true);
            }}
          >
            同步
          </Button>
          <SyncModal
            onlySync
            tmplId={tmplId}
            visible={syncVsb}
            onClose={() => setSyncVsb(false)}
            onOk={onSync}
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

const Item = (props: any) => {
  const { orgSid, teamName, disabled, item, checkprofileId, tmplId, checked, onChange } = props;
  return (
    <div className={style.package}>
      <div className={style.header}>
        {item.name.length > 18 ? (
          <Tooltip title={item.name}>
            <span className={style.name}>{item.name}</span>
          </Tooltip>
        ) : (
          <span className={style.name}>{item.name}</span>
        )}

        <Switch
          disabled={disabled}
          checked={checked}
          onChange={value => onChange(value, item.id)}
        />
      </div>
      <div className={style.labelWrapper}>
        {item.labels.map((label: any) => (
          <span key={label} className={style.label}>
            {label}
          </span>
        ))}
      </div>
      <div className={cn(style.description, style.common)}>
        <Items className={style.icon} />
        {item.description && item.description.length > 30 ? (
          <Tooltip title={item.description}>
            <Typography.Paragraph className={style.paragraph} ellipsis={{ rows: 2 }}>
              {item.description}
            </Typography.Paragraph>
          </Tooltip>
        ) : (
          <Typography.Paragraph className={style.paragraph} ellipsis={{ rows: 2 }}>
            {item.description}
          </Typography.Paragraph>
        )}
      </div>
      <div className={cn(style.language, style.common)}>
        <Globe className={style.icon} />
        <div>
          适用于 {item.languages.length} 种语言
          {item.languages.join('、').length > 20 ? (
            <Tooltip title={item.languages.join('、')}>
              <p className={style.languages}>{item.languages.join('、')}</p>
            </Tooltip>
          ) : (
            <p className={style.languages}>{item.languages.join('、')}</p>
          )}
        </div>
      </div>
      <div className={style.footer}>
        <a
          target="_blank"
          href={`${getTmplBlankRouter(
            orgSid,
            teamName,
          )}/${tmplId}/check-profiles/${checkprofileId}/pkg/${item.id}`} rel="noreferrer"
        >
          查看详细规则 <AngleRight />{' '}
        </a>
      </div>
    </div>
  );
};

export default CodeLint;
