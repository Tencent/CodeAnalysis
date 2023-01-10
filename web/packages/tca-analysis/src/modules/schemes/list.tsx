// Copyright (c) 2021-2023 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 列表
 */
import React, { useState, useRef, useEffect } from 'react';
import cn from 'classnames';
import $ from 'jquery';
import { isEmpty } from 'lodash';

import { Tooltip } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import AngleDown from 'coding-oa-uikit/lib/icon/AngleDown';
import AngleUp from 'coding-oa-uikit/lib/icon/AngleUp';
import Template from 'coding-oa-uikit/lib/icon/Template';

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
  const [height, setHeight] = useState<number | undefined>(45);

  const ref = useRef<any>(null);

  useEffect(() => {
    ref.current && setHeight($(ref.current).height());
  }, [deprecatedVsb]);

  useEffect(() => {
    setHeight(45);
    setDeprecatedVsb(false);
  }, [repoId]);

  return (
        <div className={style.schemeLeft}>
            <div className={style.schemeLeftHeader}>
                <h3>分析方案</h3>
                <button onClick={addSchemeHandle} className={style.addScheme}>
                    <PlusIcon />
                </button>
            </div>
            <div className={style.schemeLeftBody}>
                <div style={{
                  height: `calc(100% - ${height}px)`,
                  overflow: 'auto',
                }}>
                    {
                        schemeList.map(item => item.status === 1 && (
                            <SchemeItem
                                key={item.id}
                                scheme={item}
                                curScheme={scheme}
                                onClickScheme={() => changeSchemeHandle(item)}
                            />
                        ))
                    }
                </div>

                <div className={style.deprecated} ref={ref}>
                    <div
                        className={style.header}
                        onClick={() => setDeprecatedVsb(!deprecatedVsb)}
                    >
                        <h4>废弃方案</h4>
                        <span>{deprecatedVsb ? <AngleUp /> : <AngleDown />}</span>
                    </div>
                    <div className={style.deprecatedBody}>
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
                                <Tooltip title={`通过${scheme.refer_scheme.scheme_key === 'public' ? '系统' : '自定义'}模板「${scheme.refer_scheme.name}」创建`}>
                                    <Template className={cn(style.tmplIcon, { [style.sys]: scheme.refer_scheme.scheme_key === 'public' })} />
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
