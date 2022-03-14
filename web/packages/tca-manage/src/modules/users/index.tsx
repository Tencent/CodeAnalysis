import React, { useState } from 'react';
import { useHistory } from 'react-router-dom';
import { Row, Col, Tabs, Button } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { getPaginationParams, getFilterURLPath } from '@src/utils';
import { DEFAULT_PAGER } from '@src/common/constants';
import { useURLParams, useDeepEffect } from '@src/utils/hooks';
import { getUsers } from '@src/services/users';

// 模块内
import s from './style.scss';
import UserTable from './user-table';
import UserModal from './user-modal';

const { TabPane } = Tabs;

const FILTER_FIELDS: Array<string> = [];

const customFilterURLPath = (params = {}) => getFilterURLPath(FILTER_FIELDS, params);

const Jobs = () => {
  const history = useHistory();
  const [listData, setListData] = useState<Array<any>>([]);
  const [count, setCount] = useState(DEFAULT_PAGER.count);
  // const [loading, setLoading] = useState(false);
  const { filter, currentPage } = useURLParams(FILTER_FIELDS);

  const [visible, setVisible] = useState(false);
  const [selectUser, setSelectUser] = useState(null);

  const onCreateOrUpdateHandle = (user: any = null) => {
    setVisible(true);
    setSelectUser(user);
  };

  /**
     * 根据路由参数获取团队列表
     */
  const getListData = () => {
    // setLoading(true);
    getUsers(filter).then((response) => {
      setCount(response.count);
      setListData(response.results || []);
      // setLoading(false);
    });
  };

  // 当路由参数变化时触发
  useDeepEffect(() => {
    getListData();
  }, [filter]);

  // 翻页
  const onChangePageSize = (page: number, pageSize: number) => {
    const params = getPaginationParams(page, pageSize);
    history.push(customFilterURLPath(params));
  };

  return (
    <>
      <Row className={s.header} align="middle">
        <Col flex="auto">
          <Tabs defaultActiveKey="users" size="large">
            <TabPane tab={t('用户管理列表')} key="users" />
          </Tabs>
        </Col>
        <Col flex="none">
          <Button onClick={() => onCreateOrUpdateHandle()} type="primary">
            {t('创建用户')}
          </Button>
        </Col>
      </Row>
      <div className="px-lg">
        <UserModal
          visible={visible}
          onCancel={() => setVisible(false)}
          onOk={() => {
            getListData();
            setVisible(false);
          }}
          userinfo={selectUser}
        />
        <UserTable
          onEdit={onCreateOrUpdateHandle}
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            showTotal: (total: any, range: any) => `${range[0]} - ${range[1]} 条数据，共 ${total} 条`,
            onChange: onChangePageSize,
          }}
        />
      </div>
    </>
  );
};

export default Jobs;
