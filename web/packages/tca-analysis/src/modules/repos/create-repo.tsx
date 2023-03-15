/**
 * 代码库登记-弹框
 */
import React from 'react';
import { useHistory } from 'react-router-dom';
import { Modal, Form, Input, Select, message } from 'coding-oa-uikit';

import AuthFormItem from '@tencent/micro-frontend-shared/tca/user-auth/auth-form-item';
import { AuthTypeEnum, SCM_MAP } from '@tencent/micro-frontend-shared/tca/user-auth/constant';
import { getRepoName } from '@tencent/micro-frontend-shared/tca/util';
import { formScmURLSecValidate } from '@tencent/micro-frontend-shared/util';
import { userAuthAPI } from '@plat/api';
// import Authority from '@src/components/authority';
// import { SCM_MAP } from '@src/components/authority/constants';
import { postRepo } from '@src/services/repos';
import { getRepos } from '@src/services/common';
import { getAnalysisBaseRouter, getUserAuthBlankRouter } from '@src/utils/getRoutePath';
import { RestfulListAPIParams } from '@src/types';
import { REPO_TYPE } from './constant';

const { Option } = Select;

interface CreateRepoProps {
  orgSid: string;
  teamName: string;
  visible: boolean;
  onCancel: () => void;
  callback: () => void;
}

const CreateRepo = (props: CreateRepoProps) => {
  const [form] = Form.useForm();
  const { orgSid, teamName, visible, onCancel, callback } = props;

  const history = useHistory();

  const onRepoNameFocus = () => {
    const url = form.getFieldValue('scm_url');
    if (url) {
      form.setFieldsValue({
        name: getRepoName({ url }),
      });
    }
  };

  const onFinish = (formData: any) => {
    const data = {
      ...formData,
      created_from: 'codedog_web',
    };
    if (data.scm) {
      const [authType, id] = data?.scm?.split('#') ?? [];
      delete data.scm;
      data.scm_auth = { auth_type: authType };
      if (SCM_MAP[authType as AuthTypeEnum]) {
        data.scm_auth[SCM_MAP[authType as AuthTypeEnum]] = id;
      }
    }

    /** 判断代码库是否已存在，存在则提供跳转 */
    getRepos(orgSid, teamName, { limit: 1, scm_url: data.scm_url }).then(({ results }: RestfulListAPIParams) => {
      const [repo] = results;
      if (repo) {
        Modal.confirm({
          title: '代码库已登记',
          content: '该代码库已在腾讯代码分析平台完成过登记，可点击直接访问',
          okText: '直接访问',
          cancelText: '返回修改',
          onOk() {
            history.push(`${getAnalysisBaseRouter(orgSid, teamName)}/repos/${repo.id}/projects`);
          },
        });
      } else {
        postRepo(orgSid, teamName, data).then(() => {
          message.success('代码库登记成功');
          callback?.();
          onReset();
        });
      }
    });
  };

  const onReset = () => {
    form.resetFields();
    onCancel();
  };

  return (
    <Modal
      title="代码库登记"
      width={480}
      visible={visible}
      onCancel={onReset}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    // confirmLoading={loading}
    >
      <Form
        layout="vertical"
        form={form}
        initialValues={{
          scm_type: REPO_TYPE.GIT,
        }}
      >
        <Form.Item required label={'代码库地址'}>
          <Input.Group compact>
            <Form.Item name='scm_type' noStyle>
              <Select style={{ width: 70 }}>
                {
                  Object.keys(REPO_TYPE).map((key: string) => (
                    <Option key={key} value={REPO_TYPE[key]}>
                      {key}
                    </Option>
                  ))
                }
              </Select>
            </Form.Item>
            <Form.Item
              name='scm_url'
              noStyle
              rules={[
                { required: true, message: '请输入代码库地址' },
                formScmURLSecValidate,
              ]}
            >
              <Input
                style={{ width: 'calc(100% - 70px)' }}
                placeholder='代码库地址'
                onBlur={onRepoNameFocus}
              />
            </Form.Item>
          </Input.Group>
        </Form.Item>
        <Form.Item
          name="name"
          label='代码库别名'
          rules={[{ required: true, message: '请输入代码库别名' }]}
        >
          <Input placeholder='代码库别名' />
        </Form.Item>
        {/* <Authority
          form={form}
          name='scm'
          label='授权方式'
          selectStyle={{ width: 350 }}
          placeholder='选择凭证'
          addAuthRouter={getUserAuthBlankRouter()}
        /> */}
        <AuthFormItem
          form={form}
          name='scm'
          label='授权方式'
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

export default CreateRepo;
