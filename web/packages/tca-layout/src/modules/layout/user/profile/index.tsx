import React, { useState } from 'react';
import { pick } from 'lodash';
import { Layout, Form, Button, Input, message, Space, SubmitContext } from 'tdesign-react';

import UserAvatar from '@tencent/micro-frontend-shared/component/user-avatar';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { useStateStore, useDispatchStore } from '@tencent/micro-frontend-shared/hook-store';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

// 项目内
import { UserAPI } from '@plat/api';

import { t } from '@src/utils/i18n';
import { getNickName } from '@src/utils';
import { UserAction, UserState, NAMESPACE, SET_USERINFO } from '@src/store/user';

const { FormItem } = Form;

const Profile = () => {
  const dispatch = useDispatchStore<UserAction>();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const [form] = Form.useForm();
  const [edit, setEdit] = useState(false);

  // 重置
  const onReset = () => {
    setEdit(false);
    form.reset();
  };

  const onSubmit = (e: SubmitContext) => {
    if (e.validateResult === true) {
      const params = pick(e.fields, ['nickname', 'tel_number']);
      UserAPI.putUserInfo(params).then(() => {
        message.success('用户信息已更新');
        dispatch({
          type: SET_USERINFO,
          payload: {
            ...userinfo,
            ...params,
          },
        });
        onReset();
      });
    }
  };

  return (
    <>
      <PageHeader title={t('用户信息')} description={t('用户基础信息，可进行变更')} />
      <Layout.Content className='tca-pa-lg'>
        <Form style={{ width: 500 }}
          colon
          form={form}
          initialData={userinfo}
          onSubmit={onSubmit}
          resetType='initial'
          labelWidth={100}
        >
          <FormItem
            label={t('用户昵称')}
            name="nickname"
            rules={
              edit ? [{ required: true, message: t('用户昵称为必填项') }] : undefined
            }
          >
            {edit ? (
              <Input />
            ) : (
              <UserAvatar size="small" url={userinfo.avatar_url} nickname={getNickName(userinfo)} />
            )}
          </FormItem>
          {userinfo.country && (
            <FormItem label={t('城市')} name="city">
              <>
                {userinfo.country} · {userinfo.province} · {userinfo.city}
              </>
            </FormItem>
          )}
          <FormItem label={t('联系方式')} name="tel_number">
            {edit ? <Input /> : <>{userinfo.tel_number}</>}
          </FormItem>
          <FormItem label={t('创建日期')} name="create_time">
            <>{formatDateTime(userinfo.create_time)}</>
          </FormItem>
          <FormItem style={{ marginLeft: 100 }}>
            <Space>
              {edit ? (
                <>
                  <Button type="submit" key="submit">
                    {t('确定')}
                  </Button>
                  <Button onClick={onReset}>
                    {t('取消')}
                  </Button>
                </>
              ) : (
                <Button
                  key="edit"
                  onClick={() => setEdit(true)}
                >
                  {t('编辑')}
                </Button>
              )}
            </Space>
          </FormItem>
        </Form>
      </Layout.Content>
    </>
  );
};

export default Profile;
