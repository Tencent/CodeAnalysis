/**
 * 创建工具依赖
 */
import React, { useState, useEffect } from 'react';
import { isEmpty } from 'lodash';
import { Modal, Form, Input, Select, Tooltip, Button, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';

import { gScmAccounts, getSSHInfo } from '@src/services/user';
import { addToolLib, getLibDetail, updateToolLib } from '@src/services/tools';
import { AUTH_TYPE, AUTH_TYPE_TXT, REPO_TYPE_OPTIONS, REPO_TYPE } from '@src/modules/tools/constants';
// import { LIB_ENV, LIB_TYPE } from './constants';
import { LIB_ENV } from './constants';

const { TextArea } = Input;
const { Option, OptGroup } = Select;

const layout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

interface CreateToollibsProps {
  orgSid: string;
  visible: boolean;
  libId: number;
  onClose: () => void;
  callback: () => void;
}

const CreateToollibs = (props: CreateToollibsProps) => {
  const { orgSid, visible, libId, onClose, callback } = props;
  const [form] = Form.useForm();

  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [authLoading, setAuthLoading] = useState(false);
  const [detail, setDetail] = useState<any>({}); 

  const isEdit = !!libId;

  useEffect(() => {
    if (visible && isEmpty(sshAuthList) && isEmpty(httpAuthList)) {
      getAuth();
    }

    if(visible && libId && libId !== detail.id) {
      getLibDetail(orgSid, libId).then((res) => {
        setDetail(res);
        form.resetFields();
      })
    }

    if(visible) {
      form.resetFields();
    }
  }, [visible]);

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      gScmAccounts().then(r => r.results || []),
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
      })
      .finally(() => {
        setAuthLoading(false);
      });
  };

  const onFinish = (formData: any) => {
    const data = formData;
    const [authType, id] = formData?.scm_auth_id?.split('#') ?? [];
    delete data.scm_auth_id;

    data.scm_auth = { auth_type: authType };

    if (data.scm_auth.auth_type === AUTH_TYPE.HTTP) {
      data.scm_auth.scm_account = id;
    } else {
      data.scm_auth.scm_ssh = id;
    }

    data.lib_os = formData.lib_os?.join(';');

    if(isEdit) {
      updateToolLib(orgSid, libId, data).then(() => {
        message.success('更新成功');
        callback?.();
        onClose();
      })
    } else {
      addToolLib(orgSid, data).then(() => {
        message.success('创建成功');
        callback?.();
        onClose();
      })
    }
  }

  return (
    <Modal
      title={`${isEdit ? '编辑' : '添加'}工具依赖`}
      width={600}
      visible={visible}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <Form
        {...layout}
        form={form}
        initialValues={isEdit ? {
          ...detail,
          lib_os: detail?.lib_os?.split(';'),
          scm_auth_id: detail.scm_auth ? `${detail.scm_auth?.auth_type}#${detail.scm_auth?.auth_type === AUTH_TYPE.HTTP ? detail.scm_auth?.scm_account?.id : detail.scm_auth?.scm_ssh?.id}` : '',
        } : {
          scm_type: REPO_TYPE.GIT
        }}
      >
        <Form.Item
          label="依赖名称"
          name="name"
          rules={[{ required: true, message: '请输入依赖名称' }]}
        >
          <Input />
        </Form.Item>
        <Form.Item
          label="依赖描述"
          name="description"
        >
          <TextArea placeholder="长度限制256个字符。" rows={3} />
        </Form.Item>
        {/* 默认都是私有依赖，只有管理员有权限更改类型 */}
        {/* <Form.Item
          label="依赖类型"
          name="lib_type"
          rules={[{ required: true, message: '请选择依赖类型' }]}
        >
          <Select>
            {
              Object.entries(LIB_TYPE).map(([key, text]) => (
                <Option key={key} value={key}>{text}</Option>
              ))
            }
          </Select>
        </Form.Item> */}
        <Form.Item
          label="适用系统"
          name="lib_os"
        >
          <Select mode='multiple'>
            {
              Object.entries(LIB_ENV).map(([key, text]) => (
                <Option key={key} value={key}>{text}</Option>
              ))
            }
          </Select>
        </Form.Item>
        <Form.Item
          label="依赖仓库地址"
          name="scm_url"
          required
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
              rules={[
                { required: true, message: '依赖仓库地址' },
              ]}
            >
              <Input style={{ width: 357 }} />
            </Form.Item>
          </Input.Group>
        </Form.Item>
        <Form.Item label="凭证" required>
          <Form.Item noStyle name="scm_auth_id" rules={[{ required: true, message: '请选择凭证' }]}>
            <Select style={{ width: 360 }}>
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
          label="环境变量"
          name="envs"
        >
          <TextArea rows={3} />
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default CreateToollibs;