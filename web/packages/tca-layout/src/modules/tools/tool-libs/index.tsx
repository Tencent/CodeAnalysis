/**
 * 工具依赖
 */

import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router-dom';
import qs from 'qs';
import { omitBy, toNumber, omit, isString } from 'lodash';
import { Table } from 'coding-oa-uikit';

import { getQuery, formatDateTime } from '../../../utils';
import { getToolLibs } from '@src/services/tools';
import { DEFAULT_PAGER } from '../constants';

import style from './style.scss';

const Column = Table.Column;

export const ToolLibs = () => {
  const history = useHistory();
  const [list, setList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [count, setCount] = useState(DEFAULT_PAGER.count);

  const query = getQuery();
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    getListData();
  }, []);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => isString(item) && !item),
    };

    setLoading(true);
    getToolLibs(params)
      .then(response => {
        history.push(`${location.pathname}?${qs.stringify(params)}`);
        setCount(response.count);
        setList(response.results);
      })
      .finally(() => {
        setLoading(false);
      })
  }

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  return (
    <Table
      loading={loading}
      dataSource={list}
      className={style.libsTable}
      pagination={{
        current: Math.floor(pageStart / pageSize) + 1,
        total: count,
        pageSize,
        showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
        onChange: onChangePageSize
      }}
    >
      <Column
        title='依赖名称'
        dataIndex='name'
      />
      <Column
        title='环境变量'
        dataIndex='envs'
        render={(envs: any) => envs && (
          // todo: 没有按顺序遍历出环境变量，环境变量是否有顺序依赖关系？
          Object.entries(envs).map(([key, value]) => (
            <p className={style.envs} key={key}>"{key}": "{value}"</p>
          ))
        )}
      />
      <Column
        title='依赖系统'
        dataIndex='lib_os'
      />
      <Column
        title='类型'
        dataIndex='lib_type'
      />
      <Column
        title='创建时间'
        dataIndex='created_time'
        render={(time: any) => time && formatDateTime(time)}
      />
      <Column
        title='创建人'
        dataIndex='creator'
      />
    </Table>
  )
}

export default ToolLibs;