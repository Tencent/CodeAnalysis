/**
 * 工具基本信息
 */
import React, { useState, useEffect, useRef } from 'react';
import cn from 'classnames';
import { toNumber, get } from 'lodash';
import { Form, Button, Input, Checkbox, Select, message, Tag, Modal, Radio } from 'coding-oa-uikit';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';

import { formatDateTime } from '@src/utils';
import { updateTool, updateToolStatus } from '@src/services/tools';
import { AUTH_TYPE, AUTH_DICT, REPO_TYPE_OPTIONS, TOOL_STATUS, STATUSENUM, SCM_PLATFORM, AUTH_ID_PATH } from '../constants';
import { SCM_MAP } from '@src/common/constants/authority';

import Authority from '@src/components/authority';
import style from '../detail.scss';

const { TextArea } = Input;
const { Option } = Select;

const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
};

interface BaseInfoProps {
  data: any;
  orgSid: string;
  editable: boolean;
  toolId: number;
  getDetail: () => void;
}

const BaseInfo = ({ orgSid, data, editable, getDetail }: BaseInfoProps) => {
  const [form] = Form.useForm();
  const [isEdit, setIsEdit] = useState(false);

  const statusRef = useRef();

  useEffect(() => {
    form.resetFields();
    statusRef.current = data.status;
  }, [isEdit, data.id]);

  const onFinish = (formData: any) => {
    const newFormData = formData;
    if (newFormData.scm) {
      const [authType, id] = newFormData?.scm?.split('#') ?? [];
      newFormData.scm_auth = { auth_type: authType };
      if (SCM_MAP[authType]) {
        newFormData.scm_auth[SCM_MAP[authType]] = id;
      }
    } else {
      newFormData.scm_auth = null
    }
    delete newFormData.scm;

    updateTool(orgSid, data.id, {
      ...data,
      ...newFormData,
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
          scm_auth_id: `${data.scm_auth?.auth_type}#${get(data, ['scm_auth', AUTH_ID_PATH[data.scm_auth?.auth_type], 'id'])}`,
        }}
        onFinish={isEdit ? onFinish : undefined}
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
          data.scm_url && (
            <Form.Item
              label="工具仓库地址"
              required={isEdit}
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
                      rules={[
                        { required: true, message: '请输入工具仓库地址' },
                      ]}
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
                  <Authority
                    form={form}
                    name='scm'
                    label=''
                    initAuth={data.scm_auth}
                    selectStyle={{ width: 360 }}
                    placeholder='拉取代码库所需的凭证'
                  />,
                  getAuthDisplay(data.scm_auth || {}),
                )
              }
            </Form.Item>
          )
        }
        {
          data.run_cmd && (
            <Form.Item
              label="执行命令"
              name="run_cmd"
              rules={isEdit ? [{ required: true, message: '请输入执行命令' }] : undefined}
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
        {
          editable && (
            <Form.Item >
              {
                isEdit ? (
                  <>
                    <Button
                      type='primary'
                      htmlType='submit'
                      key='edit'
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
          )
        }
      </Form>
    </div>
  );
};

export default BaseInfo;
