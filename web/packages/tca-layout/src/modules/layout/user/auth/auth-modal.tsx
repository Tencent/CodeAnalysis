import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal, Form, Input, Select, message } from 'coding-oa-uikit';

// 项目内
import { AuthTypeEnum, AUTH_TYPE_OPTIONS, ScmPlatformEnum, SCM_PLATFORM_OPTIONS } from '@src/constant';
import { UserAPI } from '@plat/api';

interface AuthModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  authinfo?: any;
}

const AuthModal = ({ visible, onOk, authinfo, onCancel }: AuthModalProps) => {
  const [form] = Form.useForm();
  const isUpdate = !!authinfo;
  const { t } = useTranslation();

  // 设置默认表单scm_username字段内容
  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  /** http凭证请求操作 */
  const onHttpAuthRequest = (formData: any) => {
    if (authinfo) {
      return UserAPI.authAccount().update(authinfo.id, formData)
        .then(() => {
          message.success(t('已更新凭证'));
        });
    }
    return UserAPI.authAccount().create(formData)
      .then(() => {
        message.success(t('已录入一条新凭证'));
      });
  };

  /** ssh凭证请求操作 */
  const onSSHAuthRequest = (formData: any) => {
    const data = {
      ...formData,
      password: null,
      git_token: null,
    };

    if (authinfo) {
      return UserAPI.authSSH().update(authinfo.id, data)
        .then(() => {
          message.success(t('已更新凭证'));
        });
    }
    return UserAPI.authSSH().create(data)
      .then(() => {
        message.success(t('已录入一条新凭证'));
      });
  };

  /** 表单保存操作 */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      const promise = formData.auth_type === AuthTypeEnum.HTTP
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
            auth_type: AuthTypeEnum.HTTP,
            scm_platform: ScmPlatformEnum.TGIT,
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
                {({ getFieldValue }) => getFieldValue('scm_platform') === 7 && (
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
