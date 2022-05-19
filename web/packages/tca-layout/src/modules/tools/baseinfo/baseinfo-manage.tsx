/**
 * 工具基本信息
 */
import React, { useState, useEffect, useRef } from 'react';
import cn from 'classnames';
import { isEmpty, toNumber, find, get } from 'lodash';
import { Form, Button, Input, Checkbox, Select, Tooltip, message, Tag, Modal, Radio } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';

import { formatDateTime } from '@src/utils';
import { updateTool, updateToolStatus } from '@src/services/tools';
import { gScmAccounts, getSSHInfo, getALLOAuthInfos } from '@src/services/user';
import { AUTH_TYPE, AUTH_TYPE_TXT, AUTH_DICT, REPO_TYPE_OPTIONS, TOOL_STATUS, STATUSENUM, SCM_PLATFORM, AUTH_ID_PATH } from '../constants';

import LibScheme from './lib-scheme';
import style from '../detail.scss';

const { TextArea } = Input;
const { Option, OptGroup } = Select;

const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
};

interface BaseInfoProps {
  data: any;
  orgSid: string;
  toolId: number;
  getDetail: () => void;
}

const BaseInfo = ({ orgSid, toolId, data, getDetail }: BaseInfoProps) => {
  const [form] = Form.useForm();
  const [isEdit, setIsEdit] = useState(false);
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [OAuthList, setOAuthList] = useState<any>([]);
  const [authLoading, setAuthLoading] = useState(false);
  const statusRef = useRef();

  useEffect(() => getAuth(), []);

  useEffect(() => {
    if (!authLoading && data.id && data.scm_auth) {
      const curAuth = data.scm_auth || {};
      if (
        curAuth.scm_ssh?.id
        && curAuth.auth_type === AUTH_TYPE.SSH
        && !find(sshAuthList, { id: curAuth.scm_ssh?.id })
      ) {
        setSshAuthList([{
          ...curAuth.scm_ssh,
          authId: `${curAuth.auth_type}#${curAuth.scm_ssh?.id}`,
        }, ...sshAuthList]);
      }
      if (
        curAuth.scm_account?.id
        && curAuth.auth_type === AUTH_TYPE.HTTP
        && !find(httpAuthList, { id: curAuth.scm_account?.id })
      ) {
        setHttpAuthList([{
          ...curAuth.scm_account,
          authId: `${curAuth.auth_type}#${curAuth.scm_account?.id}`,
        }, ...httpAuthList]);
      }
      if (
        curAuth.scm_account?.id
        && curAuth.auth_type === AUTH_TYPE.OAUTH
        && !find(OAuthList, { id: curAuth.scm_account?.id })
      ) {
        setOAuthList([{
          ...curAuth.scm_oauth,
          authId: `${curAuth.auth_type}#${curAuth.scm_oauth?.id}`,
        }, ...OAuthList]);
      }
    }
  }, [authLoading, data.id]);

  useEffect(() => {
    form.resetFields();
    statusRef.current = data.status;
  }, [isEdit, data.id]);

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
        setOAuthList(result[2].map((item:any)=>({ 
          ...item, 
          authId: `${AUTH_TYPE.OAUTH}#${item.id}`,
        })));
      })
      .finally(() => {
        setAuthLoading(false);
      });
  };

  const onFinish = () => {

    const formData = form.getFieldsValue();
    const [authType, id] = formData?.scm_auth_id?.split('#') ?? [];
    delete formData.scm_auth_id;

    if (authType && id) {
      formData.scm_auth = { auth_type: authType };
      switch (formData.scm_auth.auth_type) {
        case AUTH_TYPE.HTTP:
          formData.scm_auth.scm_account = id;
          break;
        case AUTH_TYPE.SSH:
          formData.scm_auth.scm_ssh = id;
          break;
        case AUTH_TYPE.OAUTH:
          formData.scm_auth.scm_authinfo = id;
          break;
      }
    }

    updateTool(orgSid, data.id, {
      ...data,
      ...formData,
    }).then(() => {
      message.success('修改成功');
      getDetail();
      setIsEdit(false);
    });
  };

  const updateStatus = () => {
    Modal.confirm({
      title: '确认修改运营状态？',
      content: (
        <Radio.Group
          defaultValue={statusRef.current}
          onChange={(e: any) => {
            statusRef.current = e.target.value;
          }}
        >
          {
            Object.keys(TOOL_STATUS).map(item => (
              <Radio key={item} value={toNumber(item)}>{get(TOOL_STATUS, item)}</Radio>
            ))
          }
        </Radio.Group>
      ),
      onOk: () => {
        if (statusRef.current === undefined) {
          message.error('请选择运营状态');
        } else {
          updateToolStatus(orgSid, data.id, statusRef.current).then(() => {
            getDetail();
            message.success('运营状态修改成功');
          });
        }
      },
    });
  };

  const getAuthDisplay = (auth: any) => {
    if (auth.auth_type === AUTH_TYPE.HTTP) {
      return `${auth?.scm_account?.scm_username}（${AUTH_DICT[data?.scm_auth?.auth_type]}）`;
    }

    if (auth.auth_type === AUTH_TYPE.SSH) {
      return `${auth?.scm_ssh?.name}（${AUTH_DICT[data?.scm_auth?.auth_type]}）`;
    }

    if (auth.auth_type === AUTH_TYPE.OAUTH) {
      return `${get(SCM_PLATFORM, auth?.scm_oauth?.scm_platform, '其他')}（${AUTH_DICT[data?.scm_auth?.auth_type]}）`;
    }

    return '';
  };

  const getComponent = (editComponent: any, defaultData: any) => (isEdit ? editComponent : <>{defaultData}</>);

  return (
    <div>
      <Form
        {...layout}
        style={{ width: 800, padding: '20px 30px' }}
        form={form}
        initialValues={{
          ...data,
          status: STATUSENUM.NORMAL,
          scm_auth_id: `${data.scm_auth?.auth_type}#${get(data,['scm_auth',AUTH_ID_PATH[data.scm_auth?.auth_type],'id'])}`,
        }}
      >
        <Form.Item label="运营状态">
          <Tag className={cn(style.tag, style[`status${data.status}`])}>
            {get(TOOL_STATUS, data.status)}
          </Tag>
          {
            isEdit && (
              <Button
                type='link'
                className="fs-12 ml-12"
                icon={<EditIcon />}
                onClick={updateStatus}
              >修改运营状态</Button>
            )
          }
        </Form.Item>
        {
          data.name && (
            <Form.Item
              label='工具名称'
              name="name"
              rules={isEdit ? [{
                required: true,
                message: '请输入工具名称!',
              }, {
                pattern: /^[A-Za-z0-9_-]+$/,
                message: '仅支持英文、数字、中划线或下划线',
              }] : undefined}
            >
              {
                getComponent(
                  <Input placeholder="仅支持英文、数字、中划线或下划线" />,
                  data.name,
                )
              }
            </Form.Item>
          )
        }
        <Form.Item
          label='工具展示名称'
          name="display_name"
          rules={isEdit ? [{ required: true, message: '请输入前端展示名称!' }] : undefined}
        >
          {
            getComponent(
              <Input placeholder="请使用大驼峰命名，如PyLint。" />,
              data.display_name,
            )
          }
        </Form.Item>
        <Form.Item
          label='工具描述'
          name="description"
          rules={isEdit ? [{ required: true, message: '请输入工具描述!' }] : undefined}
        >
          {
            getComponent(
              <TextArea placeholder="长度限制256个字符。" rows={3} />,
              data.description,
            )
          }
        </Form.Item>
        {
          (data.scm_url || isEdit) && (
            <Form.Item
              label="工具仓库地址"
            >
              {
                getComponent(
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
                      <Input style={{ width: 486 }} />
                    </Form.Item>
                  </Input.Group>,
                  data.scm_url,
                )
              }
            </Form.Item>
          )
        }
        {
          (data.scm_auth || isEdit) && (
            <Form.Item label="凭证">
              {
                getComponent(
                  <>
                    <Form.Item noStyle name="scm_auth_id">
                      <Select style={{ width: 480 }}>
                        {!isEmpty(OAuthList) && (
                          <OptGroup label={AUTH_TYPE_TXT.OAUTH}>
                            {OAuthList.map((auth: any) => (
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
                      top: 3,
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
                  </>,
                  getAuthDisplay(data.scm_auth || {}),
                )
              }
            </Form.Item>
          )
        }
        {
          (data.run_cmd || isEdit) && (
            <Form.Item
              label="执行命令"
              name="run_cmd"
            >
              {
                getComponent(
                  <Input placeholder="该命令的工作目录为工具库根目录。" />,
                  data.run_cmd,
                )
              }
            </Form.Item>
          )
        }
        {
          (data.envs || isEdit) && (
            <Form.Item label="环境变量" name="envs">
              {
                getComponent(
                  <TextArea
                    rows={3}
                    placeholder="示例：PYTHON_HOME = $PYTHON#&_HOMEPATH = $PYTHON_HOME/bin:$PATH"
                  />,
                  data.envs,
                )
              }
            </Form.Item>
          )
        }
        <Form.Item label="License" name="license">
          {
            getComponent(
              <Input placeholder="许可证" />,
              data.license,
            )
          }
        </Form.Item>
        <LibScheme
          layout={layout}
          orgSid={orgSid}
          toolId={toolId}
          isEdit={isEdit}
          getComponent={getComponent}
        />
        <Form.Item label='语言' >
          {data.languages?.join(' | ')}
        </Form.Item>
        <Form.Item label='负责团队' >
          {data.org_detail?.name}
        </Form.Item>
        <Form.Item label='创建时间'>
          {formatDateTime(data.created_time)}
        </Form.Item>

        <Form.Item label="" name="build_flag" valuePropName="checked">
          <Checkbox disabled={!isEdit}>是否为编译型工具</Checkbox>
        </Form.Item>

        <Form.Item >
          {
            isEdit ? (
              <>
                <Button
                  type='primary'
                  key='edit'
                  onClick={() => form
                    .validateFields()
                    .then(onFinish)
                    .catch(errorInfo => {
                      // 滚动到第一个错误表单
                      form.scrollToField(errorInfo?.errorFields?.[0]?.name?.[0])
                    })
                  }
                >确认</Button>
                <Button className="ml-12" onClick={() => setIsEdit(false)}>取消</Button>
              </>
            ) : (
              <Button type='primary' onClick={() => {
                setIsEdit(true);
              }}>编辑</Button>
            )
          }
        </Form.Item>
      </Form>
    </div>
  );
};

export default BaseInfo;
