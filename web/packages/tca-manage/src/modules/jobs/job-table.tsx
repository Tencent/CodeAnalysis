import React from 'react';
import { Link } from 'react-router-dom';
import { Table, Tag, Progress } from 'coding-oa-uikit';
// import Waiting from 'coding-oa-uikit/lib/icon/Waiting';
// import Runing from 'coding-oa-uikit/lib/icon/Runing';
// import Failed from 'coding-oa-uikit/lib/icon/Failed';
// import Aborted2 from 'coding-oa-uikit/lib/icon/Aborted2';
// import Success from 'coding-oa-uikit/lib/icon/Success';
// import Attention from 'coding-oa-uikit/lib/icon/Attention';

// import DotCircle from 'coding-oa-uikit/lib/icon/DotCircle';
// import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
// import EllipsisTemplate from '@src/components/ellipsis';
import { formatDateTime, getUserName, secondToDate } from '@src/utils';
import { getJobRouter } from '@src/utils/getRoutePath';
// import OrgAndTeamAndProjectInfo from '@src/modules/components/org-team-project-info';

// 模块内
import OrgAndTeamInfo from '@src/modules/components/org-team-info';
import { STATE_CHOICES } from './constants';

const { Column } = Table;

interface IProps {
  dataSource: Array<any>;
  pagination: any;
}

const JobTable = ({ dataSource, pagination }: IProps) => (
  <>
    <Table pagination={pagination} rowKey={(item: any) => item.id} dataSource={dataSource}>
      <Column
        title={t('分析任务')}
        dataIndex="project"
        key="project"
        render={(
          { repo_scm_url, branch, organization, project_team, id, repo_id }: any,
          job: any,
        ) => (
          <>
            <Link
              className="link-name text-weight-bold"
              to={getJobRouter(
                organization?.org_sid,
                project_team?.name,
                repo_id,
                id,
                job.id,
              )}
            >
              {repo_scm_url}
            </Link>
            <div className="mt-sm fs-12 text-grey-6">
              分支：{branch} / 启动人：{getUserName(job.creator)} / 启动来源：
              {job.created_from}
            </div>
          </>
        )}
      />
      <Column
        title={t('所属团队&项目')}
        dataIndex="project"
        key="project-organization"
        render={(project: any) => (
          <OrgAndTeamInfo org={project.organization} team={project.project_team} />
        )}
      />

      {/* <Column
                    title={t('启动来源')}
                    dataIndex="created_from"
                    key="created_from"
                    render={(created_from: string) => <Tag>{created_from}</Tag>}
                />
                <Column
                    title={t('启动人')}
                    dataIndex="creator"
                    key="creator"
                    render={(creator: string) => getUserName(creator)}
                /> */}

      <Column
        title={t('执行进度')}
        dataIndex="task_num"
        key="task_num"
        render={(_: any, job: any) => (
          <div style={{ minWidth: '150px' }}>
            <Progress
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              percent={Math.floor((job.task_done / job.task_num) * 100)}
            />
          </div>
        )}
      />
      <Column
        title={t('执行状态')}
        dataIndex="state"
        key="state"
        render={(state: any) => (
          <div style={{ minWidth: '65px' }}>{STATE_CHOICES[state]}</div>
        )}
      />
      <Column
        title="执行结果"
        dataIndex="result_msg"
        render={(result_msg: any, { result_code_msg, result_code }: any) => (
          <div style={{ width: '250px' }}>
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
      <Column
        title={t('总耗时')}
        dataIndex="total_time"
        key="total_time"
        render={(_: any, job: any) => (
          <div style={{ minWidth: '180px' }}>
            <div>等待耗时：{secondToDate(job.waiting_time)}</div>
            <div>执行耗时：{secondToDate(job.execute_time)}</div>
          </div>
        )}
      />
      <Column
        title={t('创建/启动时间')}
        dataIndex="create_time"
        key="create_time"
        render={(create_time: any) => (
          <div style={{ minWidth: '150px' }}>{formatDateTime(create_time)}</div>
        )}
      />
      <Column
        title={t('启动时间')}
        dataIndex="start_time"
        key="start_time"
        render={(start_time: any) => (
          <div style={{ minWidth: '150px' }}>{formatDateTime(start_time)}</div>
        )}
      />
    </Table>
  </>
);

export default JobTable;
