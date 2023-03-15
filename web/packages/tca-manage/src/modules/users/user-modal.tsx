import React, { useRef } from 'react';
import { t } from '@src/utils/i18n';
import { Dialog, Form, Input, message, Switch, Select, notification, Button, FormInstanceFunctions } from 'tdesign-react';
import { FileCopyIcon } from 'tdesign-icons-react';
import CopyToClipboard from 'react-copy-to-clipboard';

// 项目内
import { userAPI } from '@plat/api';

// 模块内
import { LEVEL_OPTIONS, STATUS_OPTIONS } from './constants';
import { UserData } from './types';

const { FormItem } = Form;

/** 提醒 */
const openUserAccountNotification = (users: Array<any>) => {
  notification.success({
    title: '账户创建/变更提醒',
    duration: null,
    closeBtn: true,
    content: (
      <>
        {users.map((user: any, index) => (
          <div key={index} style={{ paddingTop: '10px' }}>
            <span>账户：{user.username}</span>{' '}
            <span>密码：{user.password}</span>
          </div>
        ))}
      </>
    ),
    footer: (
      <CopyToClipboard
        text={users
          .map(user => `账户：${user.username}, 密码：${user.password}`)
          .toString()}
        onCopy={() => {
          message.success('已复制全部账户信息');
        }}
      >
        <Button variant="text" icon={<FileCopyIcon />}>
          复制账户信息
        </Button>
      </CopyToClipboard>
    ),
  });
};

interface UserModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  userinfo?: UserData;
}

const UserModal = ({ userinfo, visible, onOk, onCancel }: UserModalProps) => {
  const formRef = useRef<FormInstanceFunctions>(null);

  /** 用户创建/更新请求操作 */
  const onSaveRequest = (formData: any) => {
    if (userinfo) {
      return userAPI.update(userinfo.username, {
        password: formData.password,
        is_superuser: formData.is_superuser,
        codedog_user: formData,
      }).then((response: any) => {
        message.success(t('已更新用户信息'));
        if (response.password) {
          openUserAccountNotification([response]);
        }
        return response;
      });
    }
    return userAPI.create({
      is_superuser: formData.is_superuser,
      codedog_users: [formData],
    }).then((response: any) => {
      message.success(t('已创建用户'));
      const loginUsers = response.filter((item: any) => item.password);
      if (loginUsers.length > 0) {
        openUserAccountNotification(loginUsers);
      }
      return response;
    });
  };

  /** 表单保存操作 */
  const onConfirm = () => {
    formRef.current?.validate().then((result) => {
      if (result === true) {
        const fieldsValue = formRef.current?.getFieldsValue(true);
        onSaveRequest(fieldsValue).then(() => {
          onOk();
        });
      }
    });
  };

  /** 重置表单操作 */
  const onReset = () => {
    formRef.current?.reset();
  };

  return (
    <Dialog
      header={userinfo ? t('更新用户') : t('创建用户')}
      visible={visible}
      onConfirm={onConfirm}
      onClose={onCancel}
      onOpened={onReset}
      onClosed={onReset}
    >
      <Form
        layout='vertical'
        ref={formRef}
        resetType='initial'
      >
        {userinfo && (
          <FormItem
            name="username"
            label={t('账户')}
            initialData={userinfo.username}
            rules={[{ required: true, message: t('账户为必填项') }]}
          >
            <Input disabled />
          </FormItem>
        )}
        {userinfo && (
          <FormItem name="password" label={t('更新密码')}>
            <Input type='password' />
          </FormItem>
        )}
        <FormItem
          name="nickname"
          label={userinfo ? t('昵称') : t('账户')}
          initialData={userinfo?.nickname}
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
        </FormItem>
        <FormItem name="level" label="等级" initialData={userinfo?.level}>
          <Select options={LEVEL_OPTIONS} />
        </FormItem>
        <FormItem name="status" label="状态" initialData={userinfo?.status}>
          <Select options={STATUS_OPTIONS} />
        </FormItem>
        <FormItem name="is_superuser" label="超级管理员" initialData={userinfo?.is_superuser}>
          <Switch />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default UserModal;
