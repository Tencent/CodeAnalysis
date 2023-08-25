// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 列表
 */
import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { isEmpty, debounce } from 'lodash';

import { Tooltip, Input, Button } from 'tdesign-react';
import { LayersIcon, ChevronDownIcon, ChevronUpIcon, AddIcon } from 'tdesign-icons-react';

import style from './style.scss';

interface ListProps {
  repoId: number | string;
  scheme: any;
  schemeList: any[];
  addSchemeHandle: () => void;
  changeSchemeHandle: (item: any) => void
}

const List = (props: ListProps) => {
  const { repoId, schemeList, scheme, addSchemeHandle, changeSchemeHandle } = props;
  const [deprecatedVsb, setDeprecatedVsb] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  const onSearchHandler = debounce((value: string) => {
    setSearchValue(value);
  }, 250);

  useEffect(() => {
    setDeprecatedVsb(false);
  }, [repoId]);

  return (
    <div className={style.schemeLeft}>
      <div className={style.schemeLeftHeader}>
          <h3>分析方案</h3>
          <Button icon={<AddIcon />} shape='circle' onClick={addSchemeHandle} theme='primary' />
      </div>
      <Input
        placeholder='搜索分析方案'
        className={style.searchScheme}
        onChange={onSearchHandler}
      />
      <div className={style.schemeLeftBody}>
        {
          isEmpty(schemeList) ? <p className={style.noData}>暂无数据，请先新建分析方案</p> : (
            <>
              <div className={cn(style.usedScheme, {
                [style.show]: deprecatedVsb,
                [style.hide]: !deprecatedVsb,
              })}>
                {
                  /* 搜索结果为空 */
                  searchValue
                  && isEmpty(schemeList.filter(item => item.status === 1 && item?.name?.includes(searchValue)))
                  && (
                    <p className={style.searchNoData}>未匹配到相关结果</p>
                  )
                }

                {
                  schemeList.map(item => item.status === 1 && item?.name?.includes(searchValue) && (
                    <SchemeItem
                      key={item.id}
                      scheme={item}
                      curScheme={scheme}
                      onClickScheme={() => changeSchemeHandle(item)}
                    />
                  ))
                }
              </div>
              <div className={style.deprecated}>
                <div
                  className={style.header}
                  onClick={() => setDeprecatedVsb(!deprecatedVsb)}
                >
                  <h4>
                    废弃方案（{
                      schemeList.filter(item => item.status === 2).length
                    }）
                    </h4>
                  <span>{deprecatedVsb ? <ChevronUpIcon /> : <ChevronDownIcon />}</span>
                </div>
                <div className={cn(style.deprecatedBody, {
                  [style.show]: deprecatedVsb,
                  [style.hide]: !deprecatedVsb,
                })}>
                  {
                    deprecatedVsb && schemeList.map(item => item.status === 2 && (
                      <SchemeItem
                        isDeprecated
                        key={item.id}
                        scheme={item}
                        curScheme={scheme}
                        onClickScheme={() => changeSchemeHandle(item)}
                      />
                    ))
                  }
                </div>
              </div>
            </>
          )
        }
      </div>
    </div>
  );
};

const SchemeItem = (props: any) => {
  const { scheme, curScheme, onClickScheme, isDeprecated } = props;
  return (
  <div
      key={scheme.id}
      className={cn(style.itemWrapper, { [style.active]: curScheme.id === scheme.id })}
      onClick={onClickScheme}
  >
      <div className={style.item}>
    <div className={style.title}>
        <h4 className={cn({ [style.deprecatedTitle]: isDeprecated })}>
      {scheme.name}&nbsp;
      {
          scheme.refer_scheme?.is_template && (
        <Tooltip content={`通过${scheme.refer_scheme.scheme_key === 'public' ? '系统' : '自定义'}模板「${scheme.refer_scheme.name}」创建`}>
            <LayersIcon className={cn(style.tmplIcon, { [style.sys]: scheme.refer_scheme.scheme_key === 'public' })} />
        </Tooltip>
          )
      }
        </h4>
        {scheme.default_flag && <span className={style.label}>Default</span>}
    </div>
    <div className={style.languages}>
        {
      !isEmpty(scheme.languages) && scheme.languages.map((language: string, index: number) => (
          <span
          key={language}
          className={cn({ [style.last]: scheme.languages.length === index + 1 })}
          >{language}</span>
      ))
        }
    </div>
      </div>
  </div>
  );
};

export default List;
