import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Tag, Button, Space } from 'coding-oa-uikit';
import { isEmpty, unionBy } from 'lodash';

// 项目内
import EllipsisTemplate from '@tencent/micro-frontend-shared/component/ellipsis';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import Search from '@tencent/micro-frontend-shared/component/search';
import Table from '@tencent/micro-frontend-shared/component/table';
import NodeStatus from '@tencent/micro-frontend-shared/component/node-status';
import { getNodes } from '@src/services/nodes';
import { getTeamMember } from '@src/services/team';

// 模块内
import { TAG_TYPE_COLOR, TAG_TYPE_ENUM, getNodeSearchFields } from '@src/constant';
import NodeModal from './node-modal';
import NodeTaskModal from './node-tasks-modal';

const { Column } = Table;

interface NodeTableProps {
  tagOptions: any[]
}

const NodeTable = ({ tagOptions }: NodeTableProps) => {
  const history = useHistory();
  const { orgSid }: any = useParams();

  const filterFields = getNodeSearchFields(tagOptions);
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);
  const [{ data, isLoading }, reload] = useFetch(getNodes, [orgSid, filter]);
  const { results: listData = [], count = 0 } = data || {};

  const [nodeTaskVisible, setNodeTaskVisible] = useState(false);
  const [members, setMembers] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [selectNode, setSelectNode] = useState(null);

  useEffect(() => {
    getTeamMember(orgSid).then((response: any) => {
      setMembers(unionBy(response?.admins, response?.users, 'username'));
    });
  }, []);

  const onCreateOrUpdateHandle = (node: any = null) => {
    setVisible(true);
    setSelectNode(node);
  };

  const onShowTasks = (node: any) => {
    setSelectNode(node);
    setNodeTaskVisible(true);
  };

  return (
    <>
      <NodeModal
        visible={visible}
        onCancel={() => {
          setVisible(false);
          setSelectNode(null);
        }}
        nodeinfo={selectNode}
        onOk={() => {
          reload();
          setVisible(false);
        }}
        tagOptions={tagOptions}
        members={members}
      />
      <NodeTaskModal
        visible={nodeTaskVisible}
        onCancel={() => setNodeTaskVisible(false)}
        nodeId={selectNode?.id}
      />
      <Search
        style={{ padding: '1px 0px' }}
        fields={filterFields}
        searchParams={searchParams}
        loading={false}
      />
      <Table
        pagination={{
          current: currentPage,
          total: count,
          pageSize,
        }}
        rowKey={(item: any) => item.id}
        dataSource={listData}
        scroll={{ x: true }}
        loading={isLoading}
      >
        <Column
          title={t('节点名称')}
          dataIndex="name"
          render={(name: any) => <EllipsisTemplate>{name}</EllipsisTemplate>}
        />
        <Column title={t('管理员')} dataIndex="manager" key="manager" />
        <Column
          title={t('关注人')}
          dataIndex="related_managers"
          key="related_managers"
          width={80}
          render={(related_managers: any) => (isEmpty(related_managers) ? '无' : related_managers.join(', '))}
        />
        <Column title={t('IP 地址')} dataIndex="addr" key="addr" />
        <Column
          title={t('最近上报心跳')}
          dataIndex="last_beat_time"
          key="last_beat_time"
          width={120}
          render={(last_beat_time: any) => formatDateTime(last_beat_time) || '- -'}
        />
        <Column
          title={t('所属标签')}
          dataIndex="exec_tag_details"
          key="exec_tag_details"
          render={(exec_tag_details: any) => exec_tag_details
            .map((item: any) => (<Tag
              key={item.name}
              color={item?.tag_type ? TAG_TYPE_COLOR[item?.tag_type] : TAG_TYPE_COLOR[TAG_TYPE_ENUM.PUBLIC]}
            >
              {item.display_name || item.name}
            </Tag>
            ))}
        />
        <Column
          title={t('节点状态')}
          dataIndex="enabled"
          key="enabled"
          render={(enabled: any, node: any) => <NodeStatus node={node}/>}
        />
        <Column
          title={t('操作')}
          dataIndex="op"
          render={(_: any, node: any) => (
            <Space>
              <Button
                onClick={() => onCreateOrUpdateHandle(node)}
              >
                {t('编辑')}
              </Button>
              <Button
                type="secondary"
                onClick={() => history.push(`/t/${orgSid}/nodes/${node.id}/process`)}
              >
                {t('工具进程')}
              </Button>
              <Button
                type="secondary"
                onClick={() => onShowTasks(node)}
              >
                {t('任务列表')}
              </Button>
            </Space>
          )}
        />
      </Table>
    </>
  );
};

export default NodeTable;
