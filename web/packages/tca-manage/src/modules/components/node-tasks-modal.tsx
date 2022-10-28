import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Table, Dialog, PageInfo, Tag } from 'tdesign-react';
import { get } from 'lodash';

// 项目内
import { t } from '@tencent/micro-frontend-shared/i18n';
import { getNodeTask } from '@src/services/nodes';
import { STATE_CHOICES } from '@src/modules/jobs/constants';
import EllipsisTemplate from '@tencent/micro-frontend-shared/tdesign-component/ellipsis';
import { getJobRouter } from '@plat/util';

export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  currentPage: 1,
};

interface NodeTaskModalProps {
  visible: boolean;
  nodeId: string;
  onCancel: () => void;
}

const NodeTaskModal = ({ visible, nodeId, onCancel }: NodeTaskModalProps) => {
  const [listData, setListData] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const { count, pageSize, currentPage } = pager;

  useEffect(() => {
    if (visible && nodeId) {
      getTaskList(DEFAULT_PAGER.currentPage, DEFAULT_PAGER.pageSize);
    }
  }, [nodeId]);

  const getTaskList = (page: number, pageSize: number) => {
    setLoading(true);
    getNodeTask(nodeId, {
      limit: pageSize,
      offset: (page - 1) * pageSize,
    }).then((res: any) => {
      setListData(res.results);
      setPager({
        count: res.count,
        pageSize,
        currentPage: page,
      });
      setLoading(false);
    });
  };

  const onChangePage = ({ current, pageSize }: PageInfo) => {
    setLoading(true);
    getTaskList(current, pageSize);
  };

  const columns = [
    {
      colKey: 'job',
      title: t('分析任务'),
      width: 300,
      cell: ({ row }: any) => (<>
        <Link to={getJobRouter(row)}>
          <EllipsisTemplate maxWidth={300} className="text-weight-bold">
            {get(row, ['project', 'scm_url'])}
          </EllipsisTemplate>
        </Link>
        <div className="mt-sm fs-12 text-grey-6">
          分支：{get(row, ['project', 'branch'])}
        </div>
      </>),
    },
    {
      colKey: 'task_name',
      title: t('子任务'),
      width: 100,
    },
    {
      colKey: 'state',
      title: t('执行状态'),
      width: 100,
      cell: ({ row }: any) => <div>{STATE_CHOICES[get(row, 'state')]}</div>,
    },
    {
      colKey: 'result_msg',
      title: t('执行结果'),
      width: 200,
      cell: ({ row }: any) => (
        <>
          {get(row, 'result_code') !== null && (
            <Tag theme={get(row, 'result_code') < 100 ? 'success' : 'danger'} variant='light'>
              {get(row, 'result_code_msg')}
            </Tag>
          )}
          {get(row, 'result_msg') && (
            <div className="mt-sm fs-12 text-grey-6">{get(row, 'result_msg')}</div>
          )}
        </>
      ),
    },
  ];

  return (
    <Dialog
      header={t('执行任务列表')}
      visible={visible}
      footer={null}
      onClose={onCancel}
      width={900}
    >
      <Table
        data={listData}
        loading={loading}
        columns={columns}
        pagination={{
          current: currentPage,
          total: count,
          pageSize,
          onChange: onChangePage,
        }}
        maxHeight='600px'
        size='small'
        rowKey='id'
      />
    </Dialog>
  );
};

export default NodeTaskModal;
