// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析项目 - 问题列表
 */
import React, { useState, useEffect } from 'react';
import cn from 'classnames';
// import { Link, useHistory } from 'react-router-dom';
import { useHistory } from 'react-router-dom';
import qs from 'qs';
import moment from 'moment';
import $ from 'jquery';
import { isEmpty, omit, toNumber, omitBy, cloneDeep, find, isString, invert, findIndex } from 'lodash';
import { Table, Avatar, message, Button, Modal, Tooltip, Tag, Input, Form } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

import { getQuery } from '@src/utils';
import { useProjectMembers } from '@src/utils/hooks';
import Copy from '@src/components/copy';
import { DEFAULT_PAGER } from '@src/constant';
// import { getProjectRouter } from '@src/utils/getRoutePath';
import { getIssues, handleIssues, updateIssuesAuthor } from '@src/services/projects';
import { getLintConfig, getCheckPackages } from '@src/services/schemes';

import { RESOLUTIONS, SEVERITY, SEVERITY_ENUM, ISSUE_STATUS } from '../constants';
import HandleModal from './handle-issue-modal';
import Search from './search';
import IssueModal from './issue-detail-modal';

import style from './style.scss';

const { Column } = Table;

interface SortType {
  key: string;
  order: 'ascend' | 'descend' | undefined;
}

interface IssuesProps {
  orgSid: string;
  teamName: string;
  repoId: number;
  projectId: number;
  curTab: string;
  curScheme: number;
}

const Issues = (props: IssuesProps) => {
  const history = useHistory();
  const [form] = Form.useForm();
  const [data, setData] = useState<any>({
    list: [],
    next: null,
    previous: null,
  });
  const { list, next, previous } = data;
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [selectedRowKeys, setSelectedRowKeys] = useState<any>([]);
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);
  const [pkgs, setPkgs] = useState([]);
  const [updateAuthorVsb, setUpdateAuthorVsb] = useState(false);
  const [issueModal, setIssueModal] = useState<any>({
    visible: false,
    issueId: null,
    isFirstIssue: false,  // 是否为第一个问题
    isLastIssue: false,  // 是否为最后一个问题
  });
  const { issueId } = issueModal;

  const query = getQuery();
  const { orgSid, teamName, projectId, repoId, curTab, curScheme } = props;
  const pageSize = toNumber(query.limit) || DEFAULT_PAGER.pageSize;
  const pageStart = toNumber(query.offset) || DEFAULT_PAGER.pageStart;
  const ordering: string = isString(query.ordering) ? query.ordering : '';
  const sort: SortType = {
    key: ordering.replace('-', ''),
    order: ordering.includes('-') ? 'descend' : 'ascend',
  };
  const members = useProjectMembers();

  const searchParams: any = omit(query, ['offset', 'limit']);

  useEffect(() => {
    if (curTab === 'codelint-issues') {
      getListData(pageStart, pageSize, {
        ...searchParams,
        ordering: 'severity',
      });
    }
  }, [projectId, curTab]);

  useEffect(() => {
    if (curScheme) {
      getLintConfig(orgSid, teamName, repoId, curScheme).then((res) => {
        getCheckPackages(orgSid, teamName, repoId, curScheme, {
          limit: 1000,
          checkpackage_ids: res?.checkprofile?.checkpackages?.join(','),
        }).then((response) => {
          setPkgs(response.results || []);
        });
      });
    }
  }, [curScheme, projectId]);

  const getListData = (offset = pageStart, limit = pageSize, otherParams = searchParams, callback?: any) => {
    const params = {
      offset,
      limit,
      ...omitBy(otherParams, item => !item),
    };

    setLoading(true);
    getIssues(orgSid, teamName, repoId, projectId, params)
      .then((response: any) => {
        callback?.(response.results || []);
        setCount(response.count);
        history.replace(`${location.pathname}?${qs.stringify(params)}`);
        setData({
          list: response.results || [],
          next: response.next,
          previous: response.previous,
        });
        setSelectedRowKeys([]);
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onChangePageSize = (page: number, pageSize: number) => {
    getListData((page - 1) * pageSize, pageSize);
  };

  const onShowSizeChange = (current: number, size: number) => {
    getListData(DEFAULT_PAGER.pageStart, size);
  };

  /**
   * 列表排序
   * @param pagination 分页参数
   * @param filters 过滤参数
   * @param sorter 排序参数
   * @param extra 其他
   */
  const onFilterChange = (pagination: any, filters: any, sorter: any, extra: any) => {
    if (extra.action === 'sort') {
      getListData(DEFAULT_PAGER.pageStart, pageSize, {
        ...searchParams,
        ordering: sorter.order
          ? `${sorter.order === 'descend' ? '-' : ''}${sorter.columnKey}`
          : '',
      });
    }
  };

  // 标记处理
  const handleIssue = (data: any) => {
    handleIssues(orgSid, teamName, repoId, projectId, {
      issue_ids: selectedRowKeys,
      ...data,
    }).then(() => {
      message.success('已批量更新问题状态');
      setSelectedRowKeys([]);
      getListData();
      setVisible(false);
    });
  };

  // 重新打开问题
  const reopen = () => {
    Modal.confirm({
      title: '重新打开',
      content: '是否将问题重新标记为未处理状态？',
      onOk: () => {
        handleIssues(orgSid, teamName, repoId, projectId, {
          issue_ids: selectedRowKeys,
          resolution: 0,
          scope: 1,
        }).then(() => {
          message.success('已批量更新问题状态');
          setSelectedRowKeys([]);
          getListData();
        });
      },
    });
  };

  // 批量修改责任人
  const updateAuthor = (data: any) => {
    updateIssuesAuthor(orgSid, teamName, repoId, projectId, {
      issue_ids: selectedRowKeys,
      ...data,
    }).then(() => {
      message.success('已批量更新责任人');
      setSelectedRowKeys([]);
      getListData();
      setUpdateAuthorVsb(false);
    });
  };

  useEffect(() => {
    // 弹框显示的 Issue，设置行背景
    if (issueId && issueModal.visible) {
      $(`tr[data-row-key!=${issueId}] td`).css('background-color', 'transparent');
      $(`tr[data-row-key=${issueId}] td`).css('background-color', '#f5f7fa');
    }

    if (issueModal.visible) {
      getIssueBoundary();
    }
  }, [issueModal.visible, issueId]);

  // 判断当前 Issue 是否为第一个/最后一个问题
  const getIssueBoundary = () => {
    const index = findIndex(list, { id: issueId });
    const issueStatus = {
      isFirstIssue: false,
      isLastIssue: false,
    };

    if (index === 0 && !previous) {  // 第一个问题
      issueStatus.isFirstIssue = true;
    }
    if (index === list.length - 1 && !next) { // 最后一个问题
      issueStatus.isLastIssue = true;
    }
    setIssueModal({ ...issueModal, ...issueStatus });
  };

  // Issue 弹框 - 上一个问题
  const prevIssue = () => {
    const index = findIndex(list, { id: issueId });
    if (index === 0) {
      if (previous) {  // 当前页的第一个问题，需列表请求前一页，取前一页的最后一个 issue 展示
        getListData(pageStart - pageSize, pageSize, searchParams, (data: any) => {
          setIssueModal({
            ...issueModal,
            issueId: data[data.length - 1]?.id,
          });
        });
      }
    } else {
      setIssueModal({
        ...issueModal,
        issueId: list[index - 1]?.id,
      });
    }
  };

  // Issue 弹框 - 下一个问题
  const nextIssue = () => {
    const index = findIndex(list, { id: issueId });

    if (index === list.length - 1) {
      if (next) {  // 当前页的最后一个问题，需列表请求后一页，取后一页的第一个 issue 展示
        getListData(pageStart + pageSize, pageSize, searchParams, (data: any) => {
          setIssueModal({
            ...issueModal,
            issueId: data[0]?.id,
          });
        });
      }
    } else {
      setIssueModal({
        ...issueModal,
        issueId: list[index + 1]?.id,
      });
    }
  };

  const onCloseIssueModal = () => {
    $(`tr[data-row-key=${issueId}] td`).css('background-color', 'transparent');
    setIssueModal({ visible: false, issueId: null, isFirstIssue: false, isLastIssue: false });
  };

  return (
    <>
      <Search
        pkgs={pkgs}
        searchParams={cloneDeep(searchParams)}
        loading={loading}
        callback={(params: any) => {
          getListData(DEFAULT_PAGER.pageStart, pageSize, params);
        }}
      />
      <div style={{ position: 'relative' }}>
        {!isEmpty(selectedRowKeys) && (
          <div className={style.operation}>
            <Button
              className="mr-12"
              type="link"
              onClick={() => {
                setVisible(true);
              }}
            >
              标记处理
            </Button>
            <Button className="mr-12" type="link" onClick={reopen}>
              重新打开
            </Button>
            <Button type="link" onClick={() => setUpdateAuthorVsb(true)}>
              批量修改责任人
            </Button>
          </div>
        )}
        <Table
          dataSource={list}
          rowKey={(item: any) => item.id}
          loading={loading}
          scroll={{ x: 1000 }}
          className={style.issueTable}
          onChange={onFilterChange}
          rowSelection={{
            selectedRowKeys,
            onChange: keys => setSelectedRowKeys(keys),
          }}
          pagination={{
            current: Math.floor(pageStart / pageSize) + 1,
            total: count,
            pageSize,
            showSizeChanger: true,
            showTotal: (total, range) => `${range[0]} - ${range[1]} 条，共 ${total} 条`,
            onChange: onChangePageSize,
            onShowSizeChange,
          }}
        >
          <Column
            title="所属文件"
            dataIndex="file_path"
            key="file_path"
            sorter
            sortOrder={sort.key === 'file_path' ? sort.order : undefined}
            render={(file, data: any) => file && (
              <a
                onClick={() => {
                  setIssueModal({
                    visible: true,
                    issueId: data.id,
                  });
                }}
              // target="_blank"
              // to={`${getProjectRouter(orgSid, teamName, repoId, projectId)}/codelint-issues/${
              //   data.id
              //   }`}
              >
                <p className={style.fileName}>{file.split('/').pop()}</p>
                <p className={style.path}>{file}</p>
              </a>
            )
            }
          />
          <Column
            title="规则"
            dataIndex="checkrule_real_name"
            key="checkrule_real_name"
            sorter
            sortOrder={sort.key === 'checkrule_real_name' ? sort.order : undefined}
            render={(name: any, item: any) => (
              <>
                <p>{name}</p>
                {
                  item.msg && item.msg?.length > 120
                    ? (
                      <Tooltip title={item.msg}>
                        <p className={style.path}>错误信息：{item?.msg?.substring(0, 120)}...</p>
                      </Tooltip>
                    ) : <p className={style.path}>错误信息：{item.msg}</p>
                }
              </>
            )}
          />
          <Column
            title="引入版本"
            dataIndex="revision"
            key="revision"
            render={(version: string) => version && (
              <span>
                {version.substring(0, 8)}
                <Copy
                  text={version}
                  copyText={version}
                  getPopupContainer={() => document.body}
                />
              </span>
            )
            }
          />
          <Column
            title="引入时间"
            dataIndex="ci_time"
            key="ci_time"
            sorter
            sortOrder={sort.key === 'ci_time' ? sort.order : undefined}
            render={time => time && moment(time, 'YYYY-MM-DD HH:mm').format('YYYY-MM-DD HH:mm')}
          />
          <Column
            title="问题级别"
            dataIndex="severity"
            key="severity"
            sorter
            sortOrder={sort.key === 'severity' ? sort.order : undefined}
            render={severity => (
              <Tag className={severity === 4 ? 'processing' : invert(SEVERITY_ENUM)[severity]}>
                {SEVERITY[severity]}
              </Tag>
            )}
          />
          <Column
            title="状态"
            dataIndex="state"
            key="state"
            sorter
            sortOrder={sort.key === 'state' ? sort.order : undefined}
            render={(state: number, data: any) => state && (
              <span>
                <span className={cn(style.status, style[`status-${state}`])}>
                  {RESOLUTIONS[state]}
                </span>
                {state === 2 && data.resolution && (
                  <span className={style.resolution}>
                    ({ISSUE_STATUS[data.resolution] || data.resolution})
                  </span>
                )}
              </span>
            )
            }
          />
          <Column
            title="责任人"
            dataIndex="author"
            key="author"
            render={author => (author ? (
              <>
                <Avatar size={24} icon={<UserIcon />} />{' '}
                {find(members, { username: author })
                  ? find(members, { username: author }).nickname
                  : author}
              </>
            ) : (
              '未分配'
            ))
            }
          />
        </Table>
      </div>
      <IssueModal
        visible={issueModal.visible}
        issueId={issueModal.issueId}
        issuesData={data}
        listLoading={loading}
        params={[orgSid, teamName, repoId, projectId, curScheme]}
        prevIssue={prevIssue}
        nextIssue={nextIssue}
        onClose={onCloseIssueModal}
        callback={() => getListData()}
      />
      <HandleModal visible={visible} onClose={() => setVisible(false)} onOk={handleIssue} />
      <Modal
        visible={updateAuthorVsb}
        title="批量修改责任人"
        onCancel={() => setUpdateAuthorVsb(false)}
        afterClose={() => form.resetFields()}
        onOk={() => {
          form.validateFields().then(updateAuthor);
        }}
      >
        <Form
          form={form}
          layout="vertical"
        >
          <Form.Item
            name='author'
            label='责任人'
            rules={[{ required: true, message: '请输入责任人' }]}
          >
            <Input />
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
};
export default Issues;
