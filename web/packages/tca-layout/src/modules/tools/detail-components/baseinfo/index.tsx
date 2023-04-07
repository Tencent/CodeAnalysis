/**
 * 工具基本信息
 */
import React, { useState, useEffect, useRef } from 'react';
import { t } from '@src/utils/i18n';
import cn from 'classnames';
import { get, isEmpty } from 'lodash';
import { Form, Button, Input, Checkbox, Select, message, Tag, Modal, Radio } from 'coding-oa-uikit';
import EditIcon from 'coding-oa-uikit/lib/icon/Edit';
import { formatDateTime, formScmURLSecValidate } from '@tencent/micro-frontend-shared/util';
import AuthFormItem from '@tencent/micro-frontend-shared/tca/user-auth/auth-form-item';

// 项目内
import { updateTool, updateToolStatus } from '@src/services/tools';
import {
  AuthTypeEnum, ToolStatusEnum, SCM_PLATFORM_CHOICES, AUTH_TYPE_CHOICES,
  TOOL_STATUS_OPTIONS, TOOL_STATUS_CHOICES, REPO_TYPE_OPTIONS, SCM_MAP,
} from '@src/constant';
import { userAuthAPI } from '@plat/api';
import style from '../style.scss';

const { TextArea } = Input;

const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
};

interface BaseInfoProps {
  data: any;
  orgSid: string;
  editable: boolean;
  getDetail: () => void;
}

const BaseInfo = ({ orgSid, data, editable, getDetail }: BaseInfoProps) => {
  const [form] = Form.useForm();
  const [isEdit, setIsEdit] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const statusRef = useRef();

  useEffect(() => {
    form.resetFields();
    statusRef.current = data.status;
  }, [isEdit, data.id]);

  const onFinish = (formData: any) => {
    setLoading(true);
    const newFormData = formData;
    if (newFormData.scm_auth_id) {
      const [authType, id] = newFormData?.scm_auth_id?.split('#') ?? [];
      newFormData.scm_auth = { auth_type: authType };
      if (SCM_MAP[authType as AuthTypeEnum]) {
        newFormData.scm_auth[SCM_MAP[authType as AuthTypeEnum]] = id;
      }
    } else {
      newFormData.scm_auth = null;
    }
    delete newFormData.scm_auth_id;

    updateTool(orgSid, data.id, {
      ...data,
      ...newFormData,
    }).then(() => {
      message.success(t('修改成功'));
      getDetail();
      setIsEdit(false);
    })
      .finally(() => setLoading(false));
  };

  const updateStatus = () => {
    Modal.confirm({
      title: t('确认修改运营状态？'),
      content: (
        <Radio.Group
          defaultValue={statusRef.current}
          onChange={(e: any) => {
            statusRef.current = e.target.value;
          }}
          options={TOOL_STATUS_OPTIONS}
        />
      ),
      onOk: () => {
        if (statusRef.current === undefined) {
          message.error(t('请选择运营状态'));
        } else {
          updateToolStatus(orgSid, data.id, statusRef.current).then(() => {
            getDetail();
            message.success(t('运营状态修改成功'));
          });
        }
      },
    });
  };

  const getAuthDisplay = (auth: any) => {
    if (auth?.auth_type === AuthTypeEnum.HTTP) {
      return `${get(SCM_PLATFORM_CHOICES, auth?.scm_account?.scm_platform, t('其他'))}：${auth?.scm_account?.scm_username}（${get(AUTH_TYPE_CHOICES, data?.scm_auth?.auth_type)}）`;
    }

    if (auth?.auth_type === AuthTypeEnum.SSH) {
      return `${get(SCM_PLATFORM_CHOICES, auth?.scm_ssh?.scm_platform, t('其他'))}：${auth?.scm_ssh?.name}（${get(AUTH_TYPE_CHOICES, data?.scm_auth?.auth_type)}）`;
    }

    if (auth?.auth_type === AuthTypeEnum.OAUTH) {
      return `${get(SCM_PLATFORM_CHOICES, auth?.scm_oauth?.scm_platform, t('其他'))}（${get(AUTH_TYPE_CHOICES, data?.scm_auth?.auth_type)}）`;
    }

    return '';
  };

  const getComponent = (editComponent: any, defaultData: any) => (isEdit ? editComponent : <>{defaultData}</>);

  return (
    <div>
      <Form
        {...layout}
        style={{ width: 660, padding: '20px 30px' }}
        form={form}
        initialValues={{
          ...data,
          status: ToolStatusEnum.NORMAL,
          scm_auth_id: !isEmpty(data.scm_auth) && `${data.scm_auth?.auth_type}#${get(data, ['scm_auth', get(SCM_MAP, data.scm_auth?.auth_type), 'id'])}`,
        }}
        onFinish={isEdit ? onFinish : undefined}
      >
        <Form.Item label={t('运营状态')}>
          <Tag className={cn(style.tag, style[`status${data.status}`])}>
            {get(TOOL_STATUS_CHOICES, data.status)}
          </Tag>
          {
            isEdit && (
              <Button
                type='link'
                className="fs-12 ml-12"
                icon={<EditIcon />}
                onClick={updateStatus}
              >{t('修改运营状态')}</Button>
            )
          }
        </Form.Item>
        {
          data.name && (
            <Form.Item
              label={t('工具名称')}
              name="name"
              rules={isEdit ? [{
                required: true,
                message: t('请输入工具名称!'),
              }, {
                pattern: /^[A-Za-z0-9_-]+$/,
                message: t('仅支持英文、数字、中划线或下划线'),
              }] : undefined}
            >
              {
                getComponent(
                  <Input placeholder={t('仅支持英文、数字、中划线或下划线')} />,
                  data.name,
                )
              }
            </Form.Item>
          )
        }
        <Form.Item
          label={t('工具展示名称')}
          name="display_name"
          rules={isEdit ? [{ required: true, message: t('请输入前端展示名称!') }] : undefined}
        >
          {
            getComponent(
              <Input placeholder={t('请使用大驼峰命名，如PyLint。')} />,
              data.display_name,
            )
          }
        </Form.Item>
        <Form.Item
          label={t('工具描述')}
          name="description"
          rules={isEdit ? [{ required: true, message: t('请输入工具描述!') }] : undefined}
        >
          {
            getComponent(
              <TextArea placeholder={t('长度限制256个字符。')} rows={3} />,
              data.description,
            )
          }
        </Form.Item>
        {
          data.scm_url && (
            <Form.Item
              label={t('工具仓库地址')}
              required={isEdit}
            >
              {
                getComponent(
                  <Input.Group compact>
                    <Form.Item name='scm_type' noStyle>
                      <Select style={{ width: '16%' }} options={REPO_TYPE_OPTIONS} />
                    </Form.Item>
                    <Form.Item
                      name='scm_url'
                      noStyle
                      rules={[
                        { required: true, message: t('请输入工具仓库地址') },
                        formScmURLSecValidate,
                      ]}
                    >
                      <Input style={{ width: '84%' }} />
                    </Form.Item>
                  </Input.Group>,
                  data.scm_url,
                )
              }
            </Form.Item>
          )
        }
        {
          getComponent(
            <AuthFormItem
              form={form}
              name='scm_auth_id'
              label={t('凭证')}
              userAuthAPI={userAuthAPI}
              authinfo={data.scm_auth}
              selectStyle={{ width: 360 }}
              allowClear
            />,
            data.scm_auth && (<Form.Item label={t('凭证')}>
              {getAuthDisplay(data.scm_auth)}
            </Form.Item>),
          )
        }
        {
          data.run_cmd && (
            <Form.Item
              label={t('执行命令')}
              name="run_cmd"
              rules={isEdit ? [{ required: true, message: t('请输入执行命令') }] : undefined}
            >
              {
                getComponent(
                  <Input placeholder={t('该命令的工作目录为工具库根目录。')} />,
                  data.run_cmd,
                )
              }
            </Form.Item>
          )
        }
        {
          (data.envs || isEdit) && (
            <Form.Item label={t('环境变量')} name="envs">
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
              <Input placeholder={t('许可证')} />,
              data.license,
            )
          }
        </Form.Item>

        <Form.Item label={t('语言')} >
          {data.languages?.join(' | ')}
        </Form.Item>
        <Form.Item label={t('负责团队')} >
          {data.org_detail?.name}
        </Form.Item>
        <Form.Item label={t('创建时间')}>
          {formatDateTime(data.created_time)}
        </Form.Item>

        <Form.Item label="" name="build_flag" valuePropName="checked">
          <Checkbox disabled={!isEdit}>{t('是否为编译型工具')}</Checkbox>
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
                      loading={loading}
                    >{t('确认')}</Button>
                    <Button className="ml-12" onClick={() => setIsEdit(false)}>{t('取消')}</Button>
                  </>
                ) : (
                  <Button type='primary' loading={loading} onClick={() => {
                    setIsEdit(true);
                  }}>{t('编辑')}</Button>
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
