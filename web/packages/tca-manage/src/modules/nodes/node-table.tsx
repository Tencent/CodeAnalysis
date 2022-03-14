import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { Table, Tag, Button, message } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import DangerModal from '@src/components/modal/danger-modal';
import { formatDateTime } from '@src/utils';
import { getNodes, delNode, getTags } from '@src/services/nodes';

// 模块内
import { STATUS_ENUM, STATUS_CHOICES } from './constants';
import NodeModal from './node-modal';

const { Column } = Table;

const NodeTable = () => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [tagOptions, setTagOptions] = useState<Array<any>>([]);
  const [visible, setVisible] = useState(false);
  const [selectNode, setSelectNode] = useState(null);
  const [visibleDel, setVisibleDel] = useState(false);
  const history = useHistory();

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    getNodes().then((response) => {
      setListData(response.results || []);
    });
  };

  const onDelNodeClick = (node: any = null) => {
    setVisibleDel(true)
    setSelectNode(node);
  };

  const onDelNodeHandle = (node: any) => {
    message.success(t('已删除'));
    console.log(node)
    // eslint-disable-next-line no-constant-condition
    if (false) {
      delNode(node.id).then(() => {
        message.success(t('已删除'));
        getListData();
      });
    }
  };

  useEffect(() => {
    getListData();
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
      <Table pagination={false} rowKey={(item: any) => item.id} dataSource={listData}>
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
          render={(enabled: any) => {
            let color = 'grey-5';
            if (enabled === STATUS_ENUM.ACTIVE) {
              color = 'green-5';
            } else if (enabled === STATUS_ENUM.DISACTIVE) {
              color = 'red-5';
            }
            return <span className={`text-${color}`}>{STATUS_CHOICES[enabled]}</span>;
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
