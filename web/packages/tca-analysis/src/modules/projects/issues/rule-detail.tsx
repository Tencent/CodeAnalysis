// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 规则详情
 */
import React from 'react';
import cn from 'classnames';
import { Link, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { get } from 'lodash';

import { Drawer } from 'coding-oa-uikit';
import { getToolsRouter } from '@src/utils/getRoutePath';

import style from './style.scss';

interface RuleDetailProps {
  data: any;
  visible: boolean;
  onClose: () => void;
}

const RuleDetail = (props: RuleDetailProps) => {
  const { data, visible, onClose } = props;
  const { orgSid } = useParams<any>();
  console.log(data);

  return (
    <Drawer
      title="规则详情"
      width={520}
      visible={visible}
      onClose={onClose}
      className={style.ruleDetail}
    >
      <div className={style.row}>
        <span className={style.label}>规则名称</span>
        <span>{data.real_name || '--'}</span>
      </div>

      <div className={style.row}>
        <span className={style.label}>规则概述</span>
        <span>{data.rule_title || '--'}</span>
      </div>
      <div className={style.row}>
        <span className={style.label}>所属工具</span>
        {data?.checktool?.display_name ? (
          <Link
            target="_blank"
            to={`${getToolsRouter(orgSid, data?.checktool?.id, 'baseinfo')}`}
          >
            {data?.checktool?.display_name}
          </Link>
        ) : (
          <span>--</span>
        )}
      </div>
      <div className={style.row}>
        <span className={style.label}>责任人</span>
        <span>{data.creator || '--'}</span>
      </div>
      <div className={style.row}>
        <span className={style.label}>规则状态</span>
        <span>{data.disable ? '禁用' : '活跃'}</span>
      </div>
      <div className={style.row}>
        <span className={style.label}>适用语言</span>
        <span>{data.languages?.join(' | ') || '--'}</span>
      </div>
      <div className={style.row}>
        <span className={style.label}>分类</span>
        <span>{data.category_name || '--'}</span>
      </div>
      <div className={style.row}>
        <span className={style.label}>严重级别</span>
        <span>{data.severity_name || '--'}</span>
      </div>
      <div className={cn(style.row, style.last)}>
        <span className={style.label}>详细描述</span>
      </div>
      {get(data, 'checkruledesc.desc') && (
        <div className={style.ruleDesc}>
          {/* eslint-disable-next-line */}
          <ReactMarkdown children={get(data, "checkruledesc.desc")} />
        </div>
      )}
    </Drawer>
  );
};

export default RuleDetail;
