import React, { useState, useEffect, useMemo } from 'react';
import { useHistory } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { get, isEmpty } from 'lodash';
import { Space, Button, MessagePlugin, PrimaryTableCol, TableRowData } from 'tdesign-react';
import Search from '@tencent/micro-frontend-shared/tdesign-component/search';
import Table from '@tencent/micro-frontend-shared/tdesign-component/table';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import { formatDateTime } from '@tencent/micro-frontend-shared/util/time';
import NodeStatus from '@tencent/micro-frontend-shared/tdesign-component/node-status';

// 项目内
import OrgInfo from '@plat/modules/components/org-info';
import { nodeAPI } from '@src/services/nodes';
import NodeTag from '@src/modules/components/node-tag';
import NodeTaskModal from '@src/modules/components/node-tasks-modal';
import MultiProcessModal from '@src/modules/process/multi-edit-process-modal';
import MultiNodeModal from '@src/modules/nodes/multi-edit-node-modal';
import { userAPI } from '@plat/api';

// 模块内
import { getNodeSearchFields } from './constants';
import NodeModal from './node-modal';

interface NodeTableProps {
  tagOptions: any[]
}

const NodeTable = ({ tagOptions }: NodeTableProps) => {
  const [selectNode, setSelectNode] = useState(null);
  const [visible, setVisible] = useState(false);
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [multiNodeVisible, setMultiNodeVisible] = useState(false);
  const [multiProcessVisible, setMultiProcessVisible] = useState(false);
  const [nodeTaskVisible, setNodeTaskVisible] = useState(false);
  const [members, setMembers] = useState<Array<any>>([]);
  const memberOptions = useMemo(() => members.map((item: any) => ({
    label: item.nickname,
    value: item.username,
  })), [members]);
  const hasSelectedNodes = !isEmpty(selectedRowKeys);

  const filterFields = getNodeSearchFields(tagOptions);
  const { filter, currentPage, pageSize, searchParams } = useURLParams(filterFields);

  const [{ data, isLoading }, reload] = useFetch(nodeAPI.get, [filter]);
  const { results: listData = [], count = 0 } = data || {};

  const history = useHistory();

  const onCreateOrUpdateHandle = (node: any = null) => {
    setVisible(true);
    setSelectNode(node);
  };

  useEffect(() => {
    // TODO: 此处这样limit处理不太合适，后面还是需要调整
    userAPI.get({ limit: 1000, offset: 0 }).then((response: any) => {
      setMembers(response.results);
    });
  }, []);

  const onShowTasks = (node: any) => {
    setSelectNode(node);
    setNodeTaskVisible(true);
  };

  const onMultiEditNode = () => {
    if (hasSelectedNodes) {
      setMultiNodeVisible(true);
    } else {
      MessagePlugin.warning(t('未选中任何节点'));
    }
  };

  const onMultiEditProcess = () => {
    if (hasSelectedNodes) {
      setMultiProcessVisible(true);
    } else {
      MessagePlugin.warning(t('未选中任何节点'));
    }
  };

  const columns: PrimaryTableCol<TableRowData>[] = [
    {
      colKey: 'row-select',
      type: 'multiple',
      width: 50,
      fixed: 'left',
    },
    {
      colKey: 'name',
      title: t('节点名称'),
      width: 300,
      fixed: 'left',
    },
    {
      colKey: 'organization',
      title: t('所属团队'),
      width: 120,
      cell: ({ row }: any) => <OrgInfo org={get(row, 'org_info')} />,
    },
    {
      colKey: 'manager',
      title: t('管理员'),
      width: 150,
    },
    {
      colKey: 'related_managers',
      title: t('负责人'),
      width: 150,
      cell: ({ row }: any) => (isEmpty(get(row, 'related_managers')) ? '- -' : get(row, 'related_managers').join(', ')),
    },
    {
      colKey: 'addr',
      title: t('IP 地址'),
      width: 180,
    },
    {
      colKey: 'last_beat_time',
      title: t('最近上报心跳'),
      width: 160,
      cell: ({ row }: any) => formatDateTime(get(row, 'last_beat_time')) || '- -',
    },
    {
      colKey: 'created_time',
      title: t('创建时间'),
      width: 160,
      cell: ({ row }: any) => formatDateTime(get(row, 'created_time')) || '- -',
    },
    {
      colKey: 'exec_tags',
      title: t('所属标签'),
      width: 200,
      cell: ({ row }: any) => (
        <Space size='small' breakLine>
          {get(row, 'exec_tag_details')?.map((item: any) => (
            <NodeTag key={item.name} tag={item} />
          ))}
        </Space>
      ),
    },
    {
      colKey: 'enabled',
      title: t('节点状态'),
      width: 150,
      cell: ({ row }: any) => <NodeStatus node={row} />,
    },
    {
      colKey: 'op',
      title: t('操作'),
      width: 210,
      fixed: 'right',
      cell: ({ row }: any) => (
        <Space size='small' breakLine>
          <a
            onClick={() => onCreateOrUpdateHandle(row)}
          >
            {t('编辑')}
          </a>
          <a
            onClick={() => history.push(`/manage/nodemgr/nodes/${row.id}/process`)}
          >
            {t('工具进程')}
          </a>
          <a
            onClick={() => onShowTasks(row)}
          >
            {t('任务列表')}
          </a>
        </Space>
      ),
    },
  ];

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
        memberOptions={memberOptions}
      />
      {hasSelectedNodes && <div className="py-sm px-lg">
        <Space>
          <Button onClick={onMultiEditNode}>
            {t('批量编辑节点')}
          </Button>
          <Button onClick={onMultiEditProcess}>
            {t('批量配置工具')}
          </Button>
        </Space>
      </div>}
      <Search
        fields={filterFields}
        searchParams={searchParams}
        loading={false}
        callback={() => setSelectedRowKeys([])}
      />
      <div className="px-lg">
        <Table
          rowKey='id'
          loading={isLoading}
          data={listData}
          columns={columns}
          pagination={{
            total: count,
            current: currentPage,
            pageSize,
          }}
          selectedRowKeys={selectedRowKeys}
          onSelectChange={setSelectedRowKeys}
        />
      </div>
      <MultiNodeModal
        visible={multiNodeVisible}
        onCancel={() => setMultiNodeVisible(false)}
        selectedNodes={selectedRowKeys}
        onOk={() => {
          reload();
          setMultiNodeVisible(false);
          setSelectedRowKeys([]);
        }}
        editItems={[
          {
            name: 'exec_tags',
            label: t('标签'),
            options: tagOptions,
          },
          {
            name: 'related_managers',
            label: t('关注人'),
            options: memberOptions,
            multiSelect: true,
          },
        ]}
      />
      <MultiProcessModal
        visible={multiProcessVisible}
        onCancel={() => setMultiProcessVisible(false)}
        onOk={() => {
          setMultiProcessVisible(false);
        }}
        selectedNodes={selectedRowKeys}
      />
      <NodeTaskModal
        visible={nodeTaskVisible}
        onCancel={() => setNodeTaskVisible(false)}
        nodeId={selectNode?.id}
      />
    </>
  );
};

export default NodeTable;
