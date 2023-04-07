import React, { useEffect } from 'react';
import { t } from 'i18next';
import { Modal, Form, Input, Select, message } from 'coding-oa-uikit';
import { UserAuthAPI } from './types';

// 项目内
import { AuthTypeEnum, AUTH_TYPE_OPTIONS, ScmPlatformEnum, SCM_PLATFORM_OPTIONS } from './constant';

interface AuthModalProps {
  /** 弹框开关 */
  visible: boolean;
  /** auth 接口模块 */
  userAuthAPI: UserAuthAPI;
  /** 凭证信息 */
  authinfo?: any;
  /** 确认操作 */
  onOk: () => void;
  /** 取消操作 */
  onCancel: () => void;
}

const AuthModal = ({ visible, authinfo, userAuthAPI, onOk, onCancel }: AuthModalProps) => {
  const [form] = Form.useForm();

  const isUpdate = !!authinfo;

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  /** 凭证创建/更新操作 */
  const onAuthHandler = (formData: any, type: 'ssh' | 'account') => {
    if (authinfo) {
      return { promise: userAuthAPI[type].update(authinfo.id, formData), created: false };
    }
    return { promise: userAuthAPI[type].create(formData), created: true };
  };

  /** 表单保存操作 */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      const { promise, created } = formData.auth_type === AuthTypeEnum.HTTP
        ? onAuthHandler(formData, 'account')
        : onAuthHandler({ ...formData, password: null, git_token: null }, 'ssh');
      promise.then(() => {
        created ? message.success(t('已录入一条新凭证')) : message.success(t('已更新凭证'));
        form.resetFields();
        onOk();
      });
    });
  };

  return <Modal
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
          auth_type: AuthTypeEnum.HTTP,
          scm_platform: ScmPlatformEnum.DEFAULT,
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
        {({ getFieldValue }) => (getFieldValue('auth_type') === AuthTypeEnum.SSH ? (
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
              <Select options={SCM_PLATFORM_OPTIONS} />
            </Form.Item>
            <Form.Item
              noStyle
              shouldUpdate={(prevValues, currentValues) => prevValues.scm_platform !== currentValues.scm_platform
              }
            >
              {({ getFieldValue }) => getFieldValue('scm_platform') === ScmPlatformEnum.OTHER && (
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
  </Modal>;
};

export default AuthModal;
