import React from 'react';
import { Link } from 'react-router-dom';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

interface TableProps {
  loading: boolean;
  dataSource: any[];
  orgSid: string;
}

const List = ({ loading, dataSource, orgSid }: TableProps) => (<Table
  loading={loading}
  data={dataSource}
  columns={[{
    colKey: 'display_name',
    title: '项目名称',
    cell: ({ row }) => <Link className="link-name" to={`/t/${orgSid}/p/${row.name}/repos`}>{row.display_name}</Link>,
  }, {
    colKey: 'description',
    title: '项目描述',
  }, {
    colKey: 'admins',
    title: '管理员',
    cell: ({ row }) => row.admins?.map((item: any) => item.nickname).join('、'),
  }, {
    colKey: 'created_time',
    title: '创建时间',
    cell: ({ row }) => formatDateTime(row.created_time),
  }]}
/>
);

export default List;
