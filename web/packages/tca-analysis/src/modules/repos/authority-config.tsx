/** 代码库凭证配置 */
import React from 'react';
import { Modal, Form, message, Tag } from 'coding-oa-uikit';
import AttentionRedIcon from 'coding-oa-uikit/lib/icon/AttentionRed';

import AuthFormItem from '@tencent/micro-frontend-shared/tca/user-auth/auth-form-item';
import { AuthTypeEnum, AuthTypeTxtEnum, SCM_MAP } from '@tencent/micro-frontend-shared/tca/user-auth/constant';
import { userAuthAPI } from '@plat/api';
// import Authority from '@src/components/authority';
// import { AUTH_TYPE, AUTH_TYPE_TXT, SCM_MAP } from '@src/components/authority/constants';
import { getUserAuthBlankRouter } from '@src/utils/getRoutePath';
import { putRepoAuth } from '@src/services/repos';

interface RepoAuthInfoProps {
  scmAuth: any
}

/** 用于渲染代码库凭证信息 */
const RepoAuthInfo = ({ scmAuth }: RepoAuthInfoProps) => {
  const { auth_type: authType, scm_oauth: scmOAuth, scm_ssh: scmSSH, scm_account: scmAccount } = scmAuth;
  let txt = '';
  if (authType === AuthTypeEnum.OAUTH && scmOAuth) {
    txt = `${AuthTypeTxtEnum.OAUTH}: ${scmOAuth.user?.nickname} (由 ${scmOAuth.user?.nickname} 在 ${scmOAuth.auth_origin} 创建)`;
  } else if (authType === AuthTypeEnum.SSH && scmSSH) {
    txt = `${AuthTypeTxtEnum.SSH}: ${scmSSH.name} (由 ${scmSSH.user?.nickname} 在 ${scmSSH.auth_origin} 创建)`;
  } else if (authType === AuthTypeEnum.HTTP && scmAccount) {
    txt = `${AuthTypeTxtEnum.HTTP}: ${scmAccount.scm_username} (由 ${scmAccount.user?.nickname} 在 ${scmAccount.auth_origin} 创建)`;
  }
  if (txt === '') {
    return <Tag color="error" icon={<AttentionRedIcon />}>无凭证，请尽快添加授权凭证</Tag>;
  }
  return <Tag>{txt}</Tag>;
};

interface AuthorityConfigProps {
  repoInfo: any;
  visible: boolean;
  orgSid: string;
  teamName: string;
  onCancel: () => void;
  callback?: () => void;
}

const AuthorityConfig = ({ orgSid, teamName, repoInfo, visible, onCancel, callback }: AuthorityConfigProps) => {
  const [form] = Form.useForm();

  const onFinish = ({ scm }: any) => {
    if (scm) {
      const [authType, id] = scm.split('#') ?? [];
      const scmAuth = SCM_MAP[authType as AuthTypeEnum];
      putRepoAuth(orgSid, teamName, repoInfo?.id, {
        auth_type: authType,
        [scmAuth]: id,
      }).then(() => {
        message.success('代码库凭证切换成功');
        callback?.();
        onReset();
      });
    } else {
      onCancel();
    }
  };

  const onReset = () => {
    form.resetFields();
    onCancel();
  };


  return (
    <Modal
      title="代码库凭证配置"
      width={480}
      visible={visible}
      onCancel={onReset}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form
        layout="vertical"
        form={form}
      >
        {repoInfo?.scm_auth && <Form.Item
          label='当前代码库授权凭证'
        >
          <RepoAuthInfo scmAuth={repoInfo.scm_auth} />
        </Form.Item>}
        {/* <Authority
          form={form}
          name='scm'
          label='切换授权方式'
          selectStyle={{ width: 350 }}
          placeholder='选择凭证'
          addAuthRouter={getUserAuthBlankRouter()}
        /> */}
        <AuthFormItem
          form={form}
          name='scm'
          label='切换授权方式'
          userAuthAPI={userAuthAPI}
          selectStyle={{ width: 350 }}
          placeholder='选择凭证'
          required
          addAuthRouter={getUserAuthBlankRouter()}
        />
      </Form>
    </Modal>
  );
};

export default AuthorityConfig;

