import React, { useEffect, useCallback, useState } from 'react';
import { Table } from 'coding-oa-uikit';
import { pick } from 'lodash';

import Search, { SearchFormField } from '../../../component/search';
import { Filter as FilterParams } from '../../../util/types';
import { formatDateTime } from '../../../util';

const { Column } = Table;

/** 配置默认的pager */
const DEFAULT_PAGER = {
  count: 0,
  pageStart: 0,
  pageSize: 10,
};

/** 操作日志数据结构 */
interface OperationData {
  /** ID */
  id: number;
  /** 创建人 */
  creator: string;
  /** 创建时间 */
  created_time: string;
  /** 信息 */
  message: string;
  /** 操作类型 */
  action: string
}

/** 操作日志返回结果数据结构 */
interface OperationRestfulListData {
  results: OperationData[];
  count: number;
  next: string;
  previous: string
}

export interface OperationProps {
  /** 传入的请求, 传入时需要避免副作用，通常使用useCallback包裹 */
  opRequest: (params: any) => Promise<OperationRestfulListData> | null;
  /** 筛选字段 */
  searchFields?: SearchFormField[];
  /** className */
  className?: string;
  /** style */
  style?: React.CSSProperties;
}

const Operation = ({ opRequest, searchFields, className, style }: OperationProps) => {
  /** 筛选参数 */
  const [searchParams, setSearchParams] = useState({
    limit: DEFAULT_PAGER.pageSize,
    offset: DEFAULT_PAGER.pageStart,
  });
  /** 操作日志数据 */
  const [{ loading, count, dataSource }, setData] = useState<{
    loading: boolean;
    count: number;
    dataSource: OperationData[];
  }>({ loading: false, count: 0, dataSource: [] });

  /** 获取操作日志列表数据 */
  const getListData = useCallback((params?: FilterParams) => {
    setData(pre => ({ ...pre, loading: true }));
    /** 筛选项 */
    const searchParams = {
      limit: DEFAULT_PAGER.pageSize,
      offset: DEFAULT_PAGER.pageStart,
      ...params,
    };
    setSearchParams(searchParams);
    opRequest(searchParams)?.then(({ count, results }) => {
      setData(pre => ({
        ...pre,
        count,
        dataSource: results,
      }));
    })
      .finally(() => setData(pre => ({ ...pre, loading: false })));
  }, [opRequest]);

  useEffect(() => {
    getListData();
  }, [getListData]);

  /** 筛选回调 */
  const searchCallback = useCallback((params: any) => {
    getListData(params);
  }, [getListData]);

  /** 翻页回调 */
  const tableChange = useCallback((page: number, pageSize: number = DEFAULT_PAGER.pageSize) => {
    getListData({
      ...searchParams,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    });
  }, [getListData, searchParams]);

  return <div className={className} style={style}>
    {searchFields && <Search route={false} fields={searchFields} loading={loading}
      searchParams={pick(searchParams, searchFields.map(field => field.name))} callback={searchCallback} />}
    <Table rowKey='id' loading={loading} dataSource={dataSource}
      scroll={{ x: true }}
      pagination={{
        current: Math.floor(searchParams.offset / searchParams.limit) + 1,
        total: count,
        pageSize: searchParams.limit,
        showSizeChanger: true,
        showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
        onChange: tableChange,
      }}>
      <Column
        title="操作人"
        dataIndex='creator'
        width={100}
      />
      <Column
        title="操作类型"
        dataIndex='action'
        width={200}
      />
      <Column
        title="详情"
        dataIndex='message'
      />
      <Column
        title="操作时间"
        dataIndex='created_time'
        width={200}
        render={created_time => formatDateTime(created_time)}
      />
    </Table>
  </div>;
};

export default Operation;
