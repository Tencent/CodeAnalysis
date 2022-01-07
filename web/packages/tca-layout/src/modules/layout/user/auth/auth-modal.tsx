// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 凭证创建/更新弹框
 */
import React, { useEffect } from 'react';
import { toNumber } from 'lodash';
import { Modal, Form, Input, Select, message } from 'coding-oa-uikit';

// 项目内
import { t } from '@src/i18n/i18next';
import { postScmAccounts, putScmAccount, addSSHInfo, updateSSHInfo } from '@src/services/user';
import { AUTH_TYPE, AUTH_TYPE_OPTIONS, SCM_PLATFORM } from '@src/utils/constant';

interface IProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  authinfo?: any;
}

const AuthModal = (props: IProps) => {
  const { visible, onOk, authinfo, onCancel } = props;
  const [form] = Form.useForm();
  const isUpdate = !!authinfo;

  // 设置默认表单scm_username字段内容
  useEffect(() => {
    if (visible) {
      form.resetFields();
      // form.setFieldsValue({ scm_username: authinfo ? authinfo.scm_username : null });
    }
  }, [visible]);

  /**
     * http凭证请求操作
     * @param formData 参数
     */
  const onHttpAuthRequest = (formData: any) => {
    if (authinfo) {
      return putScmAccount(authinfo.id, formData).then(() => {
        message.success(t('已更新凭证'));
      });
    }
    return postScmAccounts(formData).then(() => {
      message.success(t('已录入一条新凭证'));
    });
  };

  const onSSHAuthRequest = (formData: any) => {
    const data = {
      ...formData,
      password: null,
      git_token: null,
    };

    if (authinfo) {
      return updateSSHInfo(authinfo.id, data).then(() => {
        message.success(t('已更新凭证'));
      });
    }
    return addSSHInfo(data).then(() => {
      message.success(t('已录入一条新凭证'));
    });
  };

  /**
     * 表单保存操作
     * @param formData 参数
     */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      const promise = formData.auth_type === AUTH_TYPE.HTTP
        ? onHttpAuthRequest(formData)
        : onSSHAuthRequest(formData);
      promise.then(() => {
        form.resetFields();
        onOk();
      });
    });
  };

  return (
    <Modal
      forceRender
      title={authinfo ? t('编辑凭证') : t('录入凭证')}
      visible={visible}
      onOk={onSubmitHandle}
      afterClose={form.resetFields}
      onCancel={onCancel}
    >
      <Form
        layout={'vertical'}
        form={form}
        initialValues={
          authinfo || {
            auth_type: AUTH_TYPE.HTTP,
            scm_platform: 1,
          }
        }
      >
        <Form.Item
          name="auth_type"
          label={t('凭证类型')}
          rules={[{ required: true, message: t('凭证类型为必填项') }]}
        >
          <Select options={AUTH_TYPE_OPTIONS} disabled={isUpdate} />
        </Form.Item>
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.auth_type !== currentValues.auth_type
          }
        >
          {({ getFieldValue }) => (getFieldValue('auth_type') === AUTH_TYPE.SSH ? (
            <>
              <Form.Item
                name="name"
                label={t('凭证名称')}
                rules={[
                  { required: true, message: t('凭证名称为必填项') },
                  { max: 32, message: t('凭证名称不能超过32个字符') },
                ]}
              >
                <Input
                  disabled={isUpdate}
                  placeholder={t('请输入凭证名称，不超过32个字符')}
                />
              </Form.Item>
              <Form.Item
                name="ssh_private_key"
                label={t('SSH 私钥')}
                rules={[{ required: true, message: t('SSH 私钥为必填项') }]}
              >
                <Input.TextArea rows={3} placeholder={t('请输入SSH 私钥')} />
              </Form.Item>
            </>
          ) : (
            <>
              <Form.Item
                name="scm_username"
                label={t('用户名')}
                rules={[
                  { required: true, message: t('用户名为必填项') },
                  { max: 32, message: t('用户名不能超过32个字符') },
                ]}
              >
                <Input
                  disabled={isUpdate}
                  placeholder={t('请输入用户名，不超过32个字符')}
                />
              </Form.Item>
              <Form.Item
                name="scm_password"
                label={t('密码')}
                rules={[
                  { required: true, message: t('密码为必填项') },
                  { max: 64, message: t('密码不能超过64个字符') },
                ]}
              >
                <Input.Password placeholder={t('请输入密码，不超过64个字符')} />
              </Form.Item>
            </>
          ))
          }
        </Form.Item>
        {
          !isUpdate && (
            <>
              <Form.Item
                name="scm_platform"
                label={t('凭证来源平台')}
              >
                <Select options={Object.entries(SCM_PLATFORM).map(([value, label]) => ({
                  value: toNumber(value), label,
                }))} />
              </Form.Item>
              <Form.Item
                noStyle
                shouldUpdate={(prevValues, currentValues) => prevValues.scm_platform !== currentValues.scm_platform
                }
              >
                {({ getFieldValue }) => getFieldValue('scm_platform') === 1 && (
                  <Form.Item
                    name="scm_platform_desc"
                    label={t('其他凭证来源平台说明')}
                  >
                    <Input />
                  </Form.Item>
                )}
              </Form.Item>
            </>
          )
        }

      </Form>
    </Modal>
  );
};

export default AuthModal;
