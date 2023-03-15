import React, { useState } from 'react';
import { t } from '@src/utils/i18n';
import classnames from 'classnames';
import { pick } from 'lodash';
import { Layout, Row, Col, Form, Button, Input, message } from 'coding-oa-uikit';
import UserAvatar from '@tencent/micro-frontend-shared/component/user-avatar';
import { useStateStore, useDispatchStore } from '@tencent/micro-frontend-shared/hook-store';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

// 项目内
import { UserAction, UserState, NAMESPACE, SET_USERINFO } from '@src/store/user';
import { getNickName } from '@src/utils';
import s from '../style.scss';
import { UserAPI } from '@plat/api';

const { Content } = Layout;

const layout = {
  labelCol: { span: 6 },
};

const Profile = () => {
  const dispatch = useDispatchStore<UserAction>();
  const { userinfo } = useStateStore<UserState>(NAMESPACE);
  const [form] = Form.useForm();
  const [edit, setEdit] = useState(false);

  // 重置
  const onReset = () => {
    setEdit(false);
    form.resetFields();
  };

  const onFinish = (values: any) => {
    const params = pick(values, ['nickname', 'tel_number']);
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
  };

  return (
    <Content className="pa-lg">
      <div className={s.header}>
        <Row>
          <Col flex="auto">
            <h3 className=" fs-18">{t('用户信息')}</h3>
          </Col>
          <Col flex="200px" className=" text-right" />
        </Row>
      </div>
      <div className={classnames(s.formContent, 'mt-lg')}>
        <Form
          {...layout}
          style={{ width: '480px' }}
          form={form}
          initialValues={userinfo}
          onFinish={values => onFinish(values)}
        >
          <Form.Item
            label={t('昵称')}
            name="nickname"
            rules={
              edit ? [{ required: true, message: t('用户昵称为必填项') }] : undefined
            }
          >
            {edit ? (
              <Input width={400} />
            ) : (
              <UserAvatar size="small" url={userinfo.avatar_url} nickname={getNickName(userinfo)} />
            )}
          </Form.Item>
          {userinfo.country && (
            <Form.Item label={t('城市')} name="city">
              <>
                {userinfo.country} · {userinfo.province} · {userinfo.city}
              </>
            </Form.Item>
          )}
          <Form.Item label={t('联系方式')} name="tel_number">
            {edit ? <Input width={400} /> : <>{userinfo.tel_number}</>}
          </Form.Item>
          <Form.Item label={t('创建日期')} name="create_time">
            <>{formatDateTime(userinfo.create_time)}</>
          </Form.Item>
          <div style={{ marginTop: '30px' }}>
            {edit ? (
              <>
                <Button type="primary" htmlType="submit" key="submit">
                  {t('确定')}
                </Button>
                <Button className=" ml-12" htmlType="button" onClick={onReset}>
                  {t('取消')}
                </Button>
              </>
            ) : (
              <Button
                key="edit"
                htmlType="button"
                type="primary"
                onClick={() => setEdit(true)}
              >
                {t('编辑')}
              </Button>
            )}
          </div>
        </Form>
      </div>
    </Content>
  );
};

export default Profile;
