import React, { useRef } from 'react';
import { t } from '@src/utils/i18n';
import { get } from 'lodash';
import { Form, Input, Button, MessagePlugin, SubmitContext, FormInstanceFunctions } from 'tdesign-react';
import { UserCircleIcon, LockOnIcon } from 'tdesign-icons-react';
import { getURLSearch } from '@tencent/micro-frontend-shared/util';
// 项目内
import { postPasswordInfo } from '@src/services/common';
import { clearLoginLocalStorage, loginSuccessHandler } from '@src/utils';
import s from '@src/style.scss';

const { FormItem } = Form;

const NormalSignin = () => {
  const formRef = useRef<FormInstanceFunctions>(null);

  const onSubmit = (e: SubmitContext) => {
    if (e.validateResult === true) {
      const formValue = formRef.current?.getFieldsValue?.(true) || {};
      clearLoginLocalStorage();
      postPasswordInfo(formValue?.username, formValue?.password)
        .then((result: any) => {
          if (result.isRegister) {
            const token = get(result, 'access_token');
            const { redirect_uri: redirectUri = '' } = getURLSearch();
            loginSuccessHandler(redirectUri, token);
          } else {
            MessagePlugin.error(t('登录失败，账户或密码错误，或账户未注册'));
          }
        });
    }
  };

  return (
    <div className={s.loginBox}>
      <Form
        ref={formRef}
        layout='vertical'
        onSubmit={onSubmit}
      >
        <FormItem
          className="mb-lg"
          name="username"
          rules={[{ required: true, message: t('请输入唯一用户名') }]}
        >
          <Input clearable={true} prefixIcon={<UserCircleIcon />} placeholder={t('用户名')} />
        </FormItem>
        <FormItem className="mb-lg" name="password" rules={[{ required: true, message: t('请输入密码') }]}>
          <Input type='password' prefixIcon={<LockOnIcon />} clearable={true} placeholder={t('密码')} onEnter={() => {
            formRef.current.submit();
          }} />
        </FormItem>
        <FormItem>
          <Button theme="primary" type="submit" block>
            {t('登录')}
          </Button>
        </FormItem>
      </Form>
    </div>
  );
};

export default NormalSignin;
