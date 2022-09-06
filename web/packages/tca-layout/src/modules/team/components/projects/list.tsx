import React from 'react';
import { Link } from 'react-router-dom';
import { Table } from 'coding-oa-uikit';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

const { Column } = Table;

interface ListProps {
  loading: boolean;
  data: any[];
  orgSid: string;
}

const List = ({ loading, data, orgSid }: ListProps) => (
  <Table
    loading={loading}
    dataSource={data}
    rowKey={(item: any) => item.id}
    pagination={{
      size: 'default',
      showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
    }}
  >
    <Column
      title="项目名称"
      dataIndex="display_name"
      key="display_name"
      render={(display_name: string, data: any) => <Link className="link-name" to={`/t/${orgSid}/p/${data.name}/repos`}>{display_name}</Link>}
    />
    <Column
      title="描述"
      dataIndex="description"
      key="description"
    />
    <Column
      title="管理员"
      dataIndex="admins"
      key="admins"
      render={admins => admins?.map((item: any) => item.nickname).join('、')}
    />
    <Column
      title="创建时间"
      dataIndex="created_time"
      key="created_time"
      render={time => time && formatDateTime(time)}
    />
  </Table>
);

export default List;
