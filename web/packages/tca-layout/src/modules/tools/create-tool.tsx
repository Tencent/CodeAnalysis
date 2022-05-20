/**
 * 创建工具弹框
 */

import React, { useState, useEffect } from 'react';
import { useHistory } from 'react-router-dom';
import { isEmpty } from 'lodash';
import { Modal, Form, Input, Checkbox, Select, Tooltip, Button, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';
import { get } from 'lodash';

import { getToolsRouter } from '@src/utils/getRoutePath';
import { gScmAccounts, getSSHInfo, getALLOAuthInfos } from '@src/services/user';
import { createTool } from '@src/services/tools';
import { AUTH_TYPE, AUTH_TYPE_TXT, REPO_TYPE_OPTIONS, REPO_TYPE, SCM_PLATFORM } from './constants';


const { TextArea } = Input;
const { Option, OptGroup } = Select;

const layout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

interface CreateToolModalProps {
  orgId: string;
  visible: boolean;
  onClose: () => void;
}

const CreateToolModal = (props: CreateToolModalProps) => {
  const [form] = Form.useForm();
  const history = useHistory();
  const { orgId, visible, onClose } = props;
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [oauthAuthList, setOauthAuthList] = useState<any>([]);
  const [authLoading, setAuthLoading] = useState(false);

  useEffect(() => {
    if (visible) {
      getAuth();
    }
  }, [visible]);

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      gScmAccounts().then(r => r.results || []),
      getALLOAuthInfos().then(r => r.results || []),
    ])
      .then((result) => {
        // HTTP 和 SSH ID可能重复
        setSshAuthList(result[0]?.map((item: any) => ({
          ...item,
          authId: `${AUTH_TYPE.SSH}#${item.id}`,
        })));
        setHttpAuthList(result[1].map((item: any) => ({
          ...item,
          authId: `${AUTH_TYPE.HTTP}#${item.id}`,
        })));
        setOauthAuthList(result[2].map((item:any)=>({ 
          ...item, 
          authId: `${AUTH_TYPE.OAUTH}#${item.id}`,
        })));
      })
      .finally(() => {
        setAuthLoading(false);
      });
  };

  const onFinish = (data: any) => {
    const newFormData = data;
    const [authType, id] = data?.scm_auth_id?.split('#') ?? [];
    delete newFormData.scm_auth_id;

    newFormData.scm_auth = { auth_type: authType };

    switch (newFormData.scm_auth.auth_type) {
      case AUTH_TYPE.HTTP:
        newFormData.scm_auth.scm_account = id;
        break;
      case AUTH_TYPE.SSH:
        newFormData.scm_auth.scm_ssh = id;
        break;
      case AUTH_TYPE.OAUTH:
        newFormData.scm_auth.scm_authinfo = id;
        break;
    }

    createTool(orgId, newFormData).then((res) => {
      message.success('创建成功');
      history.push(`${getToolsRouter(orgId)}/${res.id}/tool-libs`);
    });
  };

  return (
    <Modal
      title='创建工具'
      width={600}
      visible={visible}
      // okButtonProps={{ loading }}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <Form {...layout} form={form} initialValues={{ scm_type: REPO_TYPE.GIT }}>
        <Form.Item
          label="工具名称"
          name="name"
          rules={[{
            required: true,
            message: '请输入工具名称!',
          }, {
            pattern: /^[A-Za-z0-9_-]+$/,
            message: '仅支持英文、数字、中划线或下划线',
          }]}
        >
          <Input placeholder="仅支持英文、数字、中划线或下划线" />
        </Form.Item>
        <Form.Item
          label="工具展示名称"
          name="display_name"
          rules={[{ required: true, message: '请输入前端展示名称!' }]}
        >
          <Input placeholder="请使用大驼峰命名，如PyLint。" />
        </Form.Item>
        <Form.Item
          label="工具描述"
          name="description"
          rules={[{ required: true, message: '请输入工具描述!' }]}
        >
          <TextArea placeholder="长度限制256个字符。" rows={3} />
        </Form.Item>
        <Form.Item
          label="工具仓库地址"
          name="scm_url"
        >
          <Input.Group compact>
            <Form.Item name='scm_type' noStyle>
              <Select style={{ width: 70 }}>
                {REPO_TYPE_OPTIONS.map((item: string, index) => (
                  <Option key={index} value={item}>
                    {item.toUpperCase()}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name='scm_url'
              noStyle
            >
              <Input style={{ width: 357 }} />
            </Form.Item>
          </Input.Group>
        </Form.Item>
        <Form.Item label="凭证">
          <Form.Item noStyle name="scm_auth_id">
            <Select style={{ width: 360 }}>
              {!isEmpty(oauthAuthList) && (
                <OptGroup label={AUTH_TYPE_TXT.OAUTH}>
                  {oauthAuthList.map((auth: any) => (
                    <Option
                      key={auth.authId}
                      value={auth.authId}
                      auth_type={AUTH_TYPE.OAUTH}
                    >
                      {get(SCM_PLATFORM, auth.scm_platform, '其他')}
                    </Option>
                  ))}
                </OptGroup>
              )}
              {!isEmpty(sshAuthList) && (
                <OptGroup label={AUTH_TYPE_TXT.SSH}>
                  {sshAuthList.map((auth: any) => (
                    <Option
                      key={auth.authId}
                      value={auth.authId}
                      auth_type={AUTH_TYPE.SSH}
                    >
                      {auth.name}
                    </Option>
                  ))}
                </OptGroup>
              )}
              {!isEmpty(httpAuthList) && (
                <OptGroup label={AUTH_TYPE_TXT.HTTP}>
                  {httpAuthList.map((auth: any) => (
                    <Option
                      key={auth.authId}
                      value={auth.authId}
                      auth_type={AUTH_TYPE.HTTP}
                    >
                      {auth.scm_username}
                    </Option>
                  ))}
                </OptGroup>
              )}
            </Select>
          </Form.Item>
          <div style={{
            position: 'absolute',
            top: 5,
            right: 10,
          }}>
            <Tooltip title='新增凭证' placement='top' getPopupContainer={() => document.body}>
              <Button type='link' className="mr-12" href='/user/auth' target='_blank'><PlusIcon /></Button>
            </Tooltip>
            <Tooltip title='刷新凭证' placement='top' getPopupContainer={() => document.body}>
              <Button
                type='link'
                disabled={authLoading}
                onClick={getAuth}
              ><RefreshIcon /></Button>
            </Tooltip>
          </div>
        </Form.Item>
        <Form.Item
          label="执行命令"
          name="run_cmd"
          rules={[{ required: true, message: '请输入执行命令' }]}
        >
          <Input placeholder="该命令的工作目录为工具库根目录。" />
        </Form.Item>
        <Form.Item label="环境变量" name="envs">
          <TextArea
            rows={3}
            placeholder="示例：PYTHON_HOME = $PYTHON#&_HOMEPATH = $PYTHON_HOME/bin:$PATH"
          />
        </Form.Item>
        <Form.Item label="License" name="license">
          <Input placeholder="许可证" />
        </Form.Item>
        <Form.Item label="" name="build_flag" valuePropName="checked">
          <Checkbox>是否为编译型工具</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateToolModal;
