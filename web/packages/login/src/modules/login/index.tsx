/**
 * 登录
 */
import React, { useEffect } from 'react';
import { Tabs, Form, Input, Button, message } from 'coding-oa-uikit';

import { useSelector } from 'react-redux';
import { get } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import Language from './language';
import s from './style.scss';
import { postPasswordInfo } from '@src/services/common';
import { useQuery } from '@src/utils/hooks';
import { clearLoginLocalStorage, loginSuccessHandle } from './utils';
const { TabPane } = Tabs;

const Login = () => {
  const query = useQuery();
  const APP = useSelector((state: any) => state.APP);
  const name = get(APP, 'enterprise.name', '');

  useEffect(() => {
    // 每次进来都清除storage
    clearLoginLocalStorage();
  }, []);

  const onFinish = (values: any) => {
    const { username, password } = values;
    clearLoginLocalStorage();
    postPasswordInfo(username, password)
      .then((result) => {
        if (result.isRegister) {
          const redirect = query.get('redirect_uri') || '';
          const token = get(result, 'access_token');
          loginSuccessHandle(redirect, token);
        } else {
          message.error(t('登录失败，账户或密码错误，或账户未注册'));
        }
      })
      .catch((e) => {
        message.error(e.msg || t('登录失败，请重试'));
      });
  };

  return (
    <div className={s.login}>
      <div className={s.content}>
        <Tabs className={s.body} defaultActiveKey='password' centered size="large">
          <TabPane tab={`${name} ${t('账号密码登录')}`} key='password'>
            <div className={s.loginBox}>
              <Form
                style={{ padding: '20px', textAlign: 'left' }}
                onFinish={onFinish}
              >
                <Form.Item
                  name="username"
                  rules={[{ required: true, message: t('请输入唯一用户名') }]}
                >
                  <Input placeholder={t('用户名')} />
                </Form.Item>
                <Form.Item name="password" rules={[{ required: true, message: t('请输入密码') }]}>
                  <Input.Password placeholder={t('密码')} />
                </Form.Item>
                <div style={{ marginTop: '30px' }}>
                  <Button block type="primary" size="middle" htmlType="submit" key="submit">
                    {t('登录')}
                  </Button>
                </div>
              </Form>
            </div>
          </TabPane>
        </Tabs>
      </div>
      <Language />
    </div>
  );
};
export default Login;
