/**
 * table组件，默认设置了分页器，以及分页change
 */
import React from 'react';
import { useHistory } from 'react-router-dom';
import classnames from 'classnames';
import { PrimaryTable, PrimaryTableProps, PaginationProps, PageInfo } from 'tdesign-react';
import { getPaginationParams, getURLPathByFilterParams } from '@tencent/micro-frontend-shared/util';
import { FilterField } from '@tencent/micro-frontend-shared/util/types';
import s from './style.scss';
interface RouteTableProps extends PrimaryTableProps {
  pagination: PaginationProps;
  filterFields?: FilterField[]
}

const RouteTable = (props: RouteTableProps) => {
  const { pagination, filterFields = [], className, ...otherProps } = props;
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
      scroll={{ type: 'lazy' }}
      pagination={{
        onChange,
        ...pagination,
      }}
      {...otherProps} />
  );
};

export default RouteTable;
