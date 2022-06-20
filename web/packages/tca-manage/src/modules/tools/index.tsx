import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useHistory } from 'react-router-dom';
import cn from 'classnames';
import { Tag, Button, Table, Tabs, Input, Form } from 'coding-oa-uikit';

import Filter from '@src/components/filter';
import { t } from '@src/i18n/i18next';
import { DEFAULT_PAGER } from '@src/common/constants';
import { getTools } from '@src/services/tools';
import { useDeepEffect, useURLParams } from '@src/utils/hooks';
import { formatDateTime, getPaginationParams, getFilterURLPath } from '@src/utils';
import { getToolRouter } from '@src/utils/getRoutePath';
import { STATUS_CHOICES } from './constants';

import ToolPermModal from './tool-perm-modal';
import s from './style.scss';

const { TabPane } = Tabs;
const { Column } = Table;

const FILTER_FIELDS = [
  'display_name'
];

const Tools = () => {
  const history = useHistory();
  const [form] = Form.useForm();
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  const [loading, setLoading] = useState(false);
  const [visible, setVisible] = useState(false);
  const [selectTool, setSelectTool] = useState(null);
  const { filter, currentPage, searchParams } = useURLParams(FILTER_FIELDS);

  const getListData = () => {
    setLoading(true);
    getTools(filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
    }).finally(() => {
      setLoading(false);
    })
  };

  useDeepEffect(() => {
    getListData();
  }, [filter]);

  const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  return (
    <div className="px-lg">
      <Tabs defaultActiveKey="tools" size="large">
        <TabPane tab='工具列表' key="tools">
          <Filter form={form} style={{ margin: '8px 0' }} initialValues={searchParams}>
            <Filter.Item label="" name="display_name">
              <Input.Search
                allowClear
                size="middle"
                placeholder="工具名称"
                onSearch={value => history.push(customFilterURLPath({
                  limit: DEFAULT_PAGER.pageSize,
                  offset: DEFAULT_PAGER.pageStart,
                  display_name: value
                }))}
              />
            </Filter.Item>
          </Filter>
          <Table
            loading={loading}
            rowKey={(item: any) => item.id}
            dataSource={listData}
            pagination={{
              current: currentPage,
              total: count,
              showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
              onChange: onChangePageSize,
            }}
          >
            <Column
              title={t('工具名称&简介')}
              dataIndex="display_name"
              width='50%'
              render={(display_name: string, tool: any) => (
                <>
                  <Link
                    className="link-name text-weight-bold"
                    to={{
                      pathname: getToolRouter(tool?.org_detail?.org_sid, tool.id),
                      state: { IS_MANAGE: true },
                    }}
                  >
                    {display_name}
                  </Link>
                  <div className="mt-sm fs-12 text-grey-6">
                    {tool.description}
                  </div>
                </>
              )}
            />
            <Column
              title={t('提供方')}
              dataIndex="org_detail"
              render={(org_detail: any) => <>{org_detail.name}</>}
            />
            <Column
              title={t('创建时间')}
              dataIndex="created_time"
              render={(created_time: any) => <>{formatDateTime(created_time)}</>}
            />
            <Column
              title={t('状态')}
              dataIndex="status"
              render={(status: number) => (
                <>
                  <Tag className={cn(s.toolTag, s[`status-${status}`])}>
                    {STATUS_CHOICES[status]}
                  </Tag>
                </>
              )}
            />
            <Column
              title={t('权限状态')}
              dataIndex="other"
              render={(_: any, tool: any) => {
                if (tool.open_maintain) {
                  return (
                    <>
                      <Tag className={cn(s.toolTag, s.maintain)}>支持自定义规则</Tag>{' '}
                      <Tag className={cn(s.toolTag, s.default)}>全平台可用</Tag>
                    </>
                  );
                }
                if (tool.open_user) {
                  return (
                    <>
                      <Tag className={cn(s.toolTag, s.default)}>全平台可用</Tag>
                    </>
                  );
                }
                return (
                  <>
                    <Tag className={cn(s.toolTag, s.custom)}>团队内可用</Tag>
                  </>
                );
              }}
            />
            <Column
              title={t('操作')}
              dataIndex="op"
              render={(_: any, tool: any) => (
                <Button onClick={() => {
                  setVisible(true);
                  setSelectTool(tool);
                }}>{t('权限调整')}</Button>
              )}
            />
          </Table>
          <ToolPermModal
            visible={visible}
            toolinfo={selectTool}
            onCancel={() => setVisible(false)}
            onOk={() => {
              getListData();
              setVisible(false);
            }}
          />
        </TabPane>
      </Tabs>
    </div>
  );
};

export default Tools;
