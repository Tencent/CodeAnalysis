// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { Layout, Row, Col, Form, Button, Input, Avatar, message } from 'coding-oa-uikit';
import classnames from 'classnames';
import { pick } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { useStateStore, useDispatchStore } from '@src/context/store';
import { SET_USERINFO } from '@src/context/constant';
import { putLoginUserInfo } from '@src/services/user';
import { formatDateTime, gUserImgUrl } from '@src/utils';

import s from '../style.scss';

const { Content } = Layout;

const layout = {
  labelCol: { span: 6 },
};

const Profile = () => {
  const { userinfo } = useStateStore();
  const [form] = Form.useForm();
  const [edit, setEdit] = useState(false);
  const dispatch = useDispatchStore();

  // 重置
  const onReset = () => {
    setEdit(false);
    form.resetFields();
  };

  const onFinish = (values: any) => {
    const params = {
      ...userinfo,
      ...pick(values, ['nickname', 'tel_number']),
    };
    putLoginUserInfo(params).then((res) => {
      message.success('用户信息已更新');
      dispatch({
        type: SET_USERINFO,
        payload: res,
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
              <>
                <Avatar
                  src={userinfo.avatar_url || gUserImgUrl(userinfo.uid)}
                  size="small"
                />{' '}
                <span className=" ml-sm vertical-moddle inline-block">
                  {userinfo.nickname}
                </span>
              </>
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
