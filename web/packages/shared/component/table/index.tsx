/**
 * table组件，默认设置了分页器，以及分页change
 */
import React from 'react';
import { useHistory } from 'react-router-dom';
import Table, { TableProps, TablePaginationConfig } from 'coding-oa-uikit/lib/table';
import { getPaginationParams, getURLPathByFilterParams } from '@tencent/micro-frontend-shared/util';
import { FilterField } from '@tencent/micro-frontend-shared/util/types';
import s from './style.scss';
interface RouteTableProps<RecordType> extends TableProps<RecordType> {
  pagination: TablePaginationConfig;
  filterFields?: FilterField[]
}

const RouteTable = <RecordType extends object = any>(props: RouteTableProps<RecordType>) => {
  const { pagination, filterFields = [], ...otherProps } = props;
  const history = useHistory();
  const onChange = (page: number, pageSize?: number) => {
    if (!pageSize) {
      throw new Error('pageSize is undefined');
    }
    const url = getURLPathByFilterParams(filterFields, getPaginationParams(page, pageSize));
    history.push(url);
  };
  return (
    <Table className={s.routeTable} scroll={{ x: true }} pagination={{
      showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
      onChange,
      ...pagination,
    }} rowKey={(item: any) => item.id} {...otherProps} />
  );
};

RouteTable.Column = Table.Column;

export default RouteTable;
