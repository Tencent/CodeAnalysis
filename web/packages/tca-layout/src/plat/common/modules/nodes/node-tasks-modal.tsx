import React, { useEffect, useState } from 'react';
import { t } from '@src/utils/i18n';
import { useParams } from 'react-router-dom';
import { Table, Modal, Tag } from 'coding-oa-uikit';

// 项目内
import EllipsisTemplate from '@tencent/micro-frontend-shared/component/ellipsis';
import { getNodeTask } from '@src/services/nodes';
import { TASK_STATE_CHOICES } from '@src/constant';

const { Column } = Table;

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
  const { orgSid }: any = useParams();
  const [listData, setListData] = useState<Array<any>>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [pager, setPager] = useState<any>(DEFAULT_PAGER);
  const { count, currentPage } = pager;


  useEffect(() => {
    if (visible && nodeId) {
      getTaskList(DEFAULT_PAGER.currentPage, DEFAULT_PAGER.pageSize);
    }
  }, [nodeId]);

  const getTaskList = (page: number, pageSize: number) => {
    setLoading(true);
    getNodeTask(orgSid, nodeId, {
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

  const onChangePage = (current: number, pageSize: number) => {
    setLoading(true);
    getTaskList(current, pageSize);
  };

  return (
    <Modal
      forceRender
      title={t('执行任务列表')}
      visible={visible}
      footer={null}
      onCancel={onCancel}
      width={800}
    >
      <Table
        size='small'
        rowKey={(item: any) => item.id}
        dataSource={listData}
        tableLayout='auto'
        pagination={{
          current: currentPage,
          total: count,
          onChange: onChangePage,
          simple: true,
        }}
        loading={loading}
      >
        <Column
          title={t('任务')}
          dataIndex="project"
          key="project"
          width={300}
          render={({ scm_url, branch }: any) => (
            <>
              <EllipsisTemplate maxWidth={300} className="text-weight-bold">
                {scm_url}
              </EllipsisTemplate>
              <div className="mt-sm fs-12 text-grey-6">
                分支：{branch}
              </div>
            </>
          )}
        />
        <Column
          title={t('子任务')}
          dataIndex="task_name"
          width={100}
          render={(taskName: string) => (
            <EllipsisTemplate maxWidth={100}>
              {taskName}
            </EllipsisTemplate>
          )}
        />
        <Column
          title={t('执行状态')}
          dataIndex="state"
          key="state"
          render={(state: any) => (
            <div>{TASK_STATE_CHOICES[state]}</div>
          )}
          width={100}
        />
        <Column
          title="执行结果"
          dataIndex="result_msg"
          width={200}
          render={(result_msg: any, { result_code_msg, result_code }: any) => (
            <div>
              {result_code !== null && (
                <Tag color={result_code < 100 ? 'success' : 'error'}>
                  {result_code_msg}
                </Tag>
              )}
              {result_msg && (
                <div className="mt-sm fs-12 text-grey-6">{result_msg}</div>
              )}
            </div>
          )}
        />
      </Table>
    </Modal>
  );
};

export default NodeTaskModal;
