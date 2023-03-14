/**
 * 用户管理功能
 * biz-start
 * 目前适用于体验、开源
 * biz-end
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Row, Col, Tabs, Button } from 'tdesign-react';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';

// 项目内
import { userAPI } from '@plat/api';

// 模块内
import UserTable from './user-table';
import UserModal from './user-modal';
import { UserData } from './types';
import s from '../style.scss';

const { TabPanel } = Tabs;

const Users = () => {
  const { filter, currentPage, pageSize } = useURLParams();
  const [{ data }, reload] = useFetch(userAPI.get, [filter]);
  const { results: listData = [], count = 0 } = data || {};

  const [visible, setVisible] = useState(false);
  const [selectUser, setSelectUser] = useState<UserData>(null);

  const onCreateOrUpdateHandler = (user: UserData = null) => {
    setVisible(true);
    setSelectUser(user);
  };

  return (
    <>
      <Row className={s.header} align='middle' >
        <Col flex="auto">
          <Tabs defaultValue="users" size='large'>
            <TabPanel label={t('用户管理列表')} value="users" />
          </Tabs>
        </Col>
        <Col>
          <Button onClick={() => onCreateOrUpdateHandler()} theme="primary">
            {t('创建用户')}
          </Button>
        </Col>
      </Row>
      <UserModal
        visible={visible}
        onCancel={() => setVisible(false)}
        onOk={() => {
          reload();
          setVisible(false);
        }}
        userinfo={selectUser}
      />
      <div className="px-lg">
        <UserTable
          onEdit={onCreateOrUpdateHandler}
          dataSource={listData}
          pagination={{
            current: currentPage,
            total: count,
            pageSize,
          }}
        />
      </div>
    </>
  );
};

export default Users;
