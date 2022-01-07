// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析模板入口文件
 */
import React, { useEffect, useState } from 'react';
import { useHistory, Link, useParams } from 'react-router-dom';
import { toNumber, get, find, omit, omitBy } from 'lodash';
import cn from 'classnames';
import qs from 'qs';

import { Table, Tag } from 'coding-oa-uikit';

import { getQuery } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { getTmplList } from '@src/services/template';
import { getLanguages, getTags } from '@src/services/schemes';

import Search from './search';
import Create from './create';
import style from './style.scss';

const { Column } = Table;

const Template = () => {
  const history = useHistory();
  const { org_sid: orgSid } = useParams() as any;
  const [list, setList] = useState<any>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const [tags, setTags] = useState([]);
  const [languages, setLanguages] = useState<any>([]);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getListData();

    (async () => {
      setTags(get(await getTags(), 'results', []));
      setLanguages(get(await getLanguages(), 'results', []));
    })();
  }, []);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, (item: any) => !item),
    };

    setLoading(true);
    getTmplList(orgSid, params)
      .then((response: any) => {
        setCount(response.count);
        history.push(`${location.pathname}?${qs.stringify(params)}`);
        setList(response.results || []);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  // const onShowSizeChange = (current: number, size: number) => {
  //     getListData(DEFAULT_PAGER.pageStart, size);
  // };

  return (
    <div className={style.template}>
      <Search
        searchParams={searchParams}
        loading={loading}
        createTmpl={() => setVisible(true)}
        callback={(params: any) => getListData(DEFAULT_PAGER.pageStart, pageSize, params)}
      />
      <Table
        dataSource={list}
        rowKey={(item: any) => item.id}
        loading={loading}
        scroll={{ x: 1000 }}
        // className={style.issueTable}
        pagination={{
          size: 'default',
          current: Math.floor(pageStart / pageSize) + 1,
          total: count,
          pageSize,
          showSizeChanger: true,
          showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
          onChange: onChangePageSize,
          // onShowSizeChange,
        }}
      >
        <Column
          title="模板名称"
          dataIndex="name"
          key="name"
          render={(name: string, data: any) => (
            <Link className="link-name" to={`${window.location.pathname}/${data.id}`}>
              {name}
            </Link>
          )}
        />
        <Column
          title="模板类型"
          dataIndex="scheme_key"
          key="scheme_key"
          render={(scheme_key: string) => (
            <Tag
              className={cn(style.tmplTag, { [style.sys]: scheme_key === 'public' })}
            >
              {scheme_key === 'public' ? '系统' : '自定义'}
            </Tag>
          )}
        />
        <Column
          title="语言"
          dataIndex="languages"
          key="languages"
          render={(langs: any) => langs?.map((item: any) => (find(languages, { name: item })
            ? find(languages, { name: item })?.display_name
            : item))
            .join(' | ')
          }
        />
        <Column title="描述" dataIndex="description" key="description" />
      </Table>
      <Create
        orgSid={orgSid}
        visible={visible}
        tags={tags}
        languages={languages}
        onClose={() => setVisible(false)}
      />
    </div>
  );
};

export default Template;
