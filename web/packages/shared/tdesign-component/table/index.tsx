/**
 * table组件，默认设置了分页器，以及分页change
 */
import React from 'react';
import { useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { PrimaryTable, PrimaryTableProps, PaginationProps, PageInfo, TableRowData } from 'tdesign-react';
import { getPaginationParams, getURLPathByFilterParams } from '@tencent/micro-frontend-shared/util';
import { FilterField } from '@tencent/micro-frontend-shared/util/types';
import s from './style.scss';
interface RouteTableProps<T extends TableRowData = TableRowData> extends Omit<PrimaryTableProps<T>, 'rowKey'> {
  /** row key */
  rowKey?: string
  /** 分页器 */
  pagination?: PaginationProps;
  filterFields?: FilterField[]
}

/** 路由table组件 */
const RouteTable = <T extends TableRowData = TableRowData>(props: RouteTableProps<T>) => {
  const { pagination, filterFields = [], className, rowKey = 'id', hover = true, ...otherProps } = props;
  const history = useHistory();

  const onChange = (pageInfo: PageInfo) => {
    if (!pageInfo.pageSize) {
      throw new Error('pageSize is undefined');
    }
    const url = getURLPathByFilterParams(filterFields, getPaginationParams(pageInfo.current, pageInfo.pageSize));
    history.push(url);
  };

  return (
    <PrimaryTable
      className={classnames(s.routeTable, className)}
      rowKey={rowKey}
      hover={hover}
      scroll={{ type: 'lazy' }}
      pagination={pagination ? {
        onChange,
        pageSizeOptions: [10, 20, 30, 50, 100],
        ...pagination,
      } : undefined}
      {...otherProps} />
  );
};

export default RouteTable;
