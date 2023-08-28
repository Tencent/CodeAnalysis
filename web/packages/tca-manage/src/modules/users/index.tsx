/**
 * 用户管理功能
 */
import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import { Button } from 'tdesign-react';
import { useURLParams, useFetch } from '@tencent/micro-frontend-shared/hooks';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';

// 项目内
import { userAPI } from '@plat/api';

// 模块内
import UserTable from './user-table';
import UserModal from './user-modal';
import { UserData } from './types';


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
      <PageHeader title="用户列表" description="平台全部注册用户列表" action={<Button onClick={() => onCreateOrUpdateHandler()} theme="primary">
        {t('创建用户')}
      </Button>} />
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
