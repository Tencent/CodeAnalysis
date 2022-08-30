/**
 * 创建/编辑工具依赖
 */
import React, { useState, useEffect } from 'react';
import { isEmpty, fromPairs, toPairs, get } from 'lodash';
import { Modal, Form, Input, Select, Tooltip, Button, message, Space } from 'coding-oa-uikit';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';
import Authority from '@tencent/micro-frontend-shared/component/authority';
import { UserAPI } from '@plat/api';

import { addToolLib, getLibDetail, updateToolLib } from '@src/services/tools';
import { REPO_TYPE_OPTIONS, RepoTypeEnum, SCM_MAP, LIB_ENV, LIB_TYPE } from '@src/constant';

import style from './style.scss';

const { TextArea } = Input;
const { Option } = Select;

const layout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

interface CreateToollibsProps {
  orgSid: string;
  visible: boolean;
  isSuperuser: boolean;
  libId: number;
  onClose: () => void;
  callback: () => void;
}

const CreateToollibs = (props: CreateToollibsProps) => {
  const { orgSid, visible, libId, isSuperuser, onClose, callback } = props;
  const [form] = Form.useForm();
  const [detail, setDetail] = useState<any>({});
  const isEdit = !!libId;

  useEffect(() => {
    if (visible && libId) {
      getLibDetail(orgSid, libId).then((res) => {
        setDetail(res);
        form.resetFields();
      });
    }

    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onFinish = (formData: any) => {
    const data = formData;

    if (formData.scm) {
      const [authType, id] = formData?.scm?.split('#') ?? [];
      data.scm_auth = { auth_type: authType };
      if (get(SCM_MAP, authType)) {
        data.scm_auth[get(SCM_MAP, authType)] = id;
      }
    } else {
      data.scm_auth = null;
    }
    delete data.scm;

    data.lib_os = formData.lib_os?.join(';');
    data.envs = !isEmpty(formData.envs)
      ? fromPairs(formData.envs?.map((item: { key: string, value: string }) => [item.key, item.value])) : {};

    if (isEdit) {
      updateToolLib(orgSid, libId, data).then(() => {
        message.success('更新成功');
        callback?.();
        onClose();
      });
    } else {
      addToolLib(orgSid, data).then(() => {
        message.success('创建成功');
        callback?.();
        onClose();
      });
    }
  };

  /** 表单保存操作 */
  const onSubmitHandle = () => {
    form.validateFields().then(onFinish);
  };

  return (
    <Modal
      title={`${isEdit ? '编辑' : '添加'}工具依赖`}
      width={600}
      visible={visible}
      afterClose={form.resetFields}
      onCancel={onClose}
      className={style.createModal}
      onOk={onSubmitHandle}
    >
      <Form
        {...layout}
        form={form}
        initialValues={isEdit ? {
          ...detail,
          lib_os: detail?.lib_os?.split(';'),
          envs: detail.envs ? toPairs(detail?.envs)?.map(item => ({ key: item[0], value: item[1] })) : [],
        } : {
          scm_type: RepoTypeEnum.GIT,
        }}
      >
        <Form.Item
          label={(
            <span>
              依赖名称
              <Tooltip
                getPopupContainer={() => document.body}
                title='建议包含版本号和支持的操作系统，如果各端兼容，可以不包含操作系统'
              ><QuestionCircle className={style.questionIcon} /></Tooltip>
            </span>
          )}
          name="name"
          rules={[{
            required: true,
            message: '请输入依赖名称',
          }, {
            pattern: /^[A-Za-z0-9_-]+$/,
            message: '仅支持英文、数字、中划线或下划线',
          }]}
        >
          <Input placeholder='使用英文名，示例：LINUX_JDK_8' />
        </Form.Item>
        <Form.Item
          label="依赖描述"
          name="description"
        >
          <TextArea placeholder="请简要说明依赖提供的功能，长度限制256个字符。" rows={3} />
        </Form.Item>
        {/* 默认都是私有依赖，只有超级管理员有权限更改类型 */}
        {
          isSuperuser && (
            <Form.Item
              label={(
                <span>
                  依赖类型
                  <Tooltip
                    getPopupContainer={() => document.body}
                    title={
                      <>
                        <p>私有依赖：只在当前团队中使用。</p>
                        <p>公共依赖：公开给所有团队使用。</p>
                      </>
                    }
                  ><QuestionCircle className={style.questionIcon} /></Tooltip>
                </span>
              )}
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
            </Form.Item>
          )
        }
        <Form.Item
          label="适用系统"
          name="lib_os"
          rules={[{ required: true, message: '请选择适用系统' }]}
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
              <Select style={{ width: '15%' }}>
                {REPO_TYPE_OPTIONS.map((item: any, index: number) => (
                  <Option key={index} value={item.value}>
                    {item.label}
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
              <Input style={{ width: '85%' }} />
            </Form.Item>
          </Input.Group>
        </Form.Item>
        <Authority
          form={form}
          name='scm'
          label={(
            <span>
              凭证
              <Tooltip
                getPopupContainer={() => document.body}
                title='拉取依赖仓库所需的凭证，如果是github公开仓库，可以不提供凭证。'
              ><QuestionCircle className={style.questionIcon} /></Tooltip>
            </span>
          )}
          getAuthList={[
            UserAPI.authSSH().get,
            UserAPI.authAccount().get,
            UserAPI.getOAuthInfos,
            UserAPI.getPlatformStatus,
          ]}
          initAuth={detail.scm_auth}
          selectStyle={{ width: 360 }}
          placeholder='github公开仓库可不提供凭证'
        />
        <Form.Item
          name="envs"
          label={(
            <span>
              环境变量
              <Tooltip
                getPopupContainer={() => document.body}
                title='依赖仓库拉取下来后，需要配置的环境变量。如果环境变量中用到仓库拉取后的本地目录，请使用$ROOT_DIR代替。比如需要添加到PATH中，可以设置PATH环境变量为$ROOT_DIR（执行时会添加到PATH环境变量最前面）。'
              ><QuestionCircle className={style.questionIcon} /></Tooltip>
            </span>
          )}
        >
          <Form.List name="envs">
            {(fields, { add, remove }) => (
              <>
                {fields.map(({ key, name, ...restField }) => (
                  <Space key={key} style={{ display: 'flex' }} align="baseline">
                    <Form.Item
                      {...restField}
                      name={[name, 'key']}
                      rules={[{ required: true, message: '请输入变量名' }]}
                    >
                      <Input placeholder="变量名" style={{ width: '175px' }} />
                    </Form.Item>
                    <Form.Item
                      {...restField}
                      name={[name, 'value']}
                      rules={[{ required: true, message: '请输入变量值' }]}
                    >
                      <Input placeholder="变量值" style={{ width: '175px' }} />
                    </Form.Item>
                    <Tooltip title='移除'>
                      <Button
                        type='text'
                        style={{ marginLeft: '3px' }}
                        onClick={() => remove(name)}
                      ><TrashIcon /></Button>
                    </Tooltip>
                  </Space>
                ))}
                <Form.Item>
                  <Button type="dashed" onClick={() => add()} block >
                    添加环境变量
                  </Button>
                </Form.Item>
              </>
            )}
          </Form.List>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateToollibs;
