import React, { useEffect } from 'react';
import { Modal, Form, Input, message, Switch, Select, notification, Button } from 'coding-oa-uikit';
import Copy from 'coding-oa-uikit/lib/icon/Copy';
import CopyToClipboard from 'react-copy-to-clipboard';

// 项目内
import { t } from '@src/i18n/i18next';
import { postUsers, putUser } from '@src/services/users';

// 模块内
import { LEVEL_OPTIONS, STATUS_OPTIONS } from './constants';

interface IProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  userinfo: any;
}

const openNotificationWithIcon = (users: Array<any>) => {
  notification.success({
    message: '账户创建/变更提醒',
    duration: null,
    description: (
      <>
        {users.map((user: any, index) => (
          <div key={index} className="mb-sm">
            <span>账户：{user.username}</span>{' '}
            <span className="ml-sm">密码：{user.password}</span>
          </div>
        ))}
        <CopyToClipboard
          text={users
            .map(user => `账户：${user.username}, 密码：${user.password}`)
            .toString()}
          onCopy={() => message.success('已复制全部账户信息')}
        >
          <Button className="mt-md" type="secondary" icon={<Copy />}>
            复制账户信息
          </Button>
        </CopyToClipboard>
      </>
    ),
  });
};

const UserModal = ({ userinfo, visible, onOk, onCancel }: IProps) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onSaveRequest = (formData: any) => {
    if (userinfo) {
      return putUser(userinfo.username, {
        password: formData.password,
        is_superuser: formData.is_superuser,
        codedog_user: formData,
      }).then((response) => {
        if (response.password) {
          openNotificationWithIcon([response]);
        }
        message.success(t('已更新用户信息'));

        return response;
      });
    }
    return postUsers({
      is_superuser: formData.is_superuser,
      codedog_users: [formData],
    }).then((response) => {
      message.success(t('已创建用户'));
      const loginUsers = response.filter((item: any) => item.password);
      if (loginUsers.length > 0) {
        openNotificationWithIcon(loginUsers);
      }
      return response;
    });
  };

  /**
     * 表单保存操作
     * @param formData 参数
     */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      onSaveRequest(formData).then(() => {
        onOk();
      });
    });
  };

  return (
    <Modal
      forceRender
      title={userinfo ? t('更新用户') : t('创建用户')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Form layout={'vertical'} form={form} initialValues={userinfo || {}}>
        {userinfo && (
          <Form.Item
            name="username"
            label={t('账户')}
            rules={[{ required: true, message: t('账户为必填项') }]}
          >
            <Input disabled />
          </Form.Item>
        )}
        {userinfo && (
          <Form.Item name="password" label={t('更新密码')}>
            <Input />
          </Form.Item>
        )}
        <Form.Item
          name="nickname"
          label={userinfo ? t('昵称') : t('账户')}
          rules={
            userinfo
              ? [
                {
                  required: true,
                  message: t('用户昵称为必填项'),
                },
              ]
              : [
                {
                  required: true,
                  message: t('账户为必填项'),
                },
                {
                  pattern: /^[\w.@+-]+$/,
                  message: t('仅支持英文、数字、邮箱等'),
                },
              ]
          }
        >
          <Input />
        </Form.Item>
        <Form.Item name="level" label="等级">
          <Select options={LEVEL_OPTIONS} />
        </Form.Item>
        <Form.Item name="status" label="状态">
          <Select options={STATUS_OPTIONS} />
        </Form.Item>
        <Form.Item name="is_superuser" label="超级管理员" valuePropName="checked">
          <Switch />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default UserModal;
