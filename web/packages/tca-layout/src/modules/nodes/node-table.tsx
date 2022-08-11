import React, { useState, useEffect } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Table, Tag, Button, Space } from 'coding-oa-uikit';
import { isEmpty, union } from 'lodash';

import Loading from 'coding-oa-uikit/lib/icon/Loading'
import Stop from 'coding-oa-uikit/lib/icon/Stop'
import ExclamationCircle from 'coding-oa-uikit/lib/icon/ExclamationCircle'
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle'

// 项目内
import { t } from '@src/i18n/i18next';
import EllipsisTemplate from '@src/components/ellipsis';
import { formatDateTime, getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useDeepEffect, useURLParams } from '@src/utils/hooks';
import { getNodes, getTags } from '@src/services/nodes';
import { getTeamMember } from '@src/services/team';

// 模块内
import { STATUS_ENUM, STATE_ENUM, TAG_TYPE_COLOR, TAG_TYPE_ENUM } from './constants';
import NodeModal from './node-modal';
import NodeTaskModal from './node-tasks-modal';

import s from './style.scss';
import Search from './node-search';

const FILTER_FIELDS = [
  'name',
  'manager',
  'exec_tags',
  'state',
  'enabled'
];

const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

const { Column } = Table;

const NodeTable = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState(false);
  const [tagOptions, setTagOptions] = useState<Array<any>>([]);
  const [nodeTaskVisible, setNodeTaskVisible] = useState(false);
  const [members, setMembers] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [selectNode, setSelectNode] = useState(null);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);
  const history = useHistory();
  const { orgSid }: any = useParams();

  /**
   * 根据路由参数获取团队列表
   */
  const getListData = () => {
    setLoading(true);
    getNodes(orgSid, filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
    }).finally(() => {
      setLoading(false);
    })
  };

  useEffect(() => {
    getTags(orgSid).then((response) => {
      setTagOptions(response.results.map((item: any) => ({
        text: item.display_name || item.name,
        value: item.name,
      })));
    });
    getTeamMember(orgSid).then((response) => {
      setMembers(union(response?.admins, response?.users));
    });
  }, []);

  const onCreateOrUpdateHandle = (node: any = null) => {
    setVisible(true);
    setSelectNode(node);
  };

  // 当路由参数变化时触发
  useDeepEffect(() => {
    getListData();
  }, [filter]);

  // 筛选
  const onSearch = (params: any) => {
    history.push(customFilterURLPath({
      limit: DEFAULT_PAGER.pageSize,
      offset: DEFAULT_PAGER.pageStart,
      ...params,
    }));
  };

  const onShowTasks = (node: any) => {
    setSelectNode(node);
    setNodeTaskVisible(true);
  };

  // 翻页
  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  return (
    <>
      <NodeModal
        visible={visible}
        onCancel={() => setVisible(false)}
        nodeinfo={selectNode}
        onOk={() => {
          getListData();
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
      <div className={s.filter}>
        <Search loading={loading} searchParams={searchParams} tagOptions={tagOptions} callback={onSearch} />
      </div>
      <Table pagination={{
        current: currentPage,
        total: count,
        showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
        onChange: onChangePageSize,
      }} rowKey={(item: any) => item.id} dataSource={listData} scroll={{ x: true }} >
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
          render={(related_managers: any) => isEmpty(related_managers) ? '无' : related_managers.join(', ')}
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
          render={(exec_tag_details: any) => exec_tag_details.map((item: any) =>
            <Tag
              key={item.name}
              color={item?.tag_type ? TAG_TYPE_COLOR[item?.tag_type] : TAG_TYPE_COLOR[TAG_TYPE_ENUM.PUBLIC]}
            >
              {item.display_name || item.name}
            </Tag>
          )}
        />
        <Column
          title={t('节点状态')}
          dataIndex="enabled"
          key="enabled"
          render={(enabled: any, node: any) => {
            if (enabled === STATUS_ENUM.ACTIVE && node.state === STATE_ENUM.BUSY) {
              return <Tag icon={<Loading />} color='processing'>{t('运行中')}</Tag>
            } else if (enabled === STATUS_ENUM.ACTIVE) {
              return <Tag icon={<DotCircle />} color='success'>{t('在线')}</Tag>
            } else if (enabled === STATUS_ENUM.DISACTIVE) {
              return <Tag icon={<Stop />}>{t('失效')}</Tag>
            } else {
              return <Tag icon={<ExclamationCircle />} color='warning'>{t('离线')}</Tag>
            }
          }}
        />
        <Column
          title={t('其他操作')}
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
