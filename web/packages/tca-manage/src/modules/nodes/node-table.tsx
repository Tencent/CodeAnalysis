import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { Table, Tag, Button, message } from 'coding-oa-uikit';

import Loading from 'coding-oa-uikit/lib/icon/Loading'
import Stop from 'coding-oa-uikit/lib/icon/Stop'
import ExclamationCircle from 'coding-oa-uikit/lib/icon/ExclamationCircle'
import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle'


// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';
import { formatDateTime, getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useDeepEffect, useURLParams } from '@src/utils/hooks';
import { getNodes, delNode, getTags } from '@src/services/nodes';

// 模块内
import { STATUS_ENUM, STATE_ENUM } from './constants';
import NodeModal from './node-modal';

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
  const [visible, setVisible] = useState(false);
  const [selectNode, setSelectNode] = useState(null);
  const [visibleDel, setVisibleDel] = useState(false);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);
  const history = useHistory();

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    setLoading(true);
    getNodes(filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
    }).finally(() => {
      setLoading(false);
    })
  };

  const onDelNodeClick = (node: any = null) => {
    setVisibleDel(true)
    setSelectNode(node);
  };

  const onDelNodeHandle = (node: any) => {
    delNode(node.id).then(() => {
      message.success(t('已删除'));
      getListData();
    });
  };

  useEffect(() => {
    getTags().then((response) => {
      setTagOptions(response.results.map((item: any) => ({
        text: item.name,
        value: item.name,
      })));
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
      />
      <DangerModal
        title={t('删除节点')}
        visible={visibleDel}
        onCancel={() => setVisibleDel(false)}
        onOk={() => onDelNodeHandle(selectNode)}
        content={
          <div>
            {t('确认删除节点')}{' '}
            <Tag color="default">{selectNode?.name}</Tag>{' '}
            {t('？')}
          </div>
        }
      />
      <div className={s.filterContent}>
        <Search loading={loading} searchParams={searchParams} tagOptions={tagOptions} callback={onSearch} />
      </div>
      <Table pagination={{

        current: currentPage,
        total: count,
        showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
        onChange: onChangePageSize,
      }} rowKey={(item: any) => item.id} dataSource={listData}>
        <Column title={t('节点名称')} dataIndex="name" />
        <Column title={t('负责人')} dataIndex="manager" key="manager" />
        <Column title={t('IP 地址')} dataIndex="addr" key="addr" />
        <Column
          title={t('最近上报心跳')}
          dataIndex="last_beat_time"
          key="last_beat_time"
          render={(last_beat_time: any) => formatDateTime(last_beat_time) || '- -'}
        />
        <Column
          title={t('所属标签')}
          dataIndex="exec_tags"
          key="exec_tags"
          render={(exec_tags: any) => exec_tags.map((tag: string) => <Tag key={tag}>{tag}</Tag>)
          }
        />
        <Column
          title={t('节点状态')}
          dataIndex="enabled"
          key="enabled"
          render={(enabled: any, node: any) => {
            if (enabled === STATUS_ENUM.ACTIVE && node.state === STATE_ENUM.BUSY) {
              return <Tag icon={<Loading spin />} color='processing'>运行中</Tag>
            } else if (enabled === STATUS_ENUM.ACTIVE) {
              return <Tag icon={<DotCircle spin />} color='success'>在线</Tag>
            } else if (enabled === STATUS_ENUM.DISACTIVE) {
              return <Tag icon={<Stop spin />}>失效</Tag>
            } else {
              return <Tag icon={<ExclamationCircle spin />} color='warning'>离线</Tag>
            }
          }}
        />
        <Column
          title={t('其他操作')}
          dataIndex="op"
          render={(_: any, node: any) => (
            <div style={{ width: '280px' }}>
              <Button
                className="mr-sm"
                onClick={() => onCreateOrUpdateHandle(node)}
              >
                {t('编辑')}
              </Button>
              <Button
                className="mr-sm"
                danger
                onClick={() => {
                  onDelNodeClick(node)
                }}
              >
                {t('删除')}
              </Button>
              <Button
                type="secondary"
                onClick={() => history.push(`/manage/nodes/${node.id}/process`)}
              >
                {t('工具进程配置')}
              </Button>
            </div>
          )}
        />
      </Table>
    </>
  );
};

export default NodeTable;
