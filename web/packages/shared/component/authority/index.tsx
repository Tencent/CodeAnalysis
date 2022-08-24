/**
 * 选择认证
 */
import React, { useState, useEffect } from 'react';
import { find, isEmpty, filter, get } from 'lodash';
import { Button, Form, Select, Tooltip } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';

import { AUTH_TYPE, AUTH_TYPE_TXT, SCM_MAP, SCM_PLATFORM_CHOICES } from './constants';

import { FormInstance } from 'rc-field-form';
const { Option, OptGroup } = Select;

interface AuthorityProps {
  name: string; // 对应表单 name
  form: FormInstance; // form 对象
  label: string | React.ReactNode; // FormItem label
  getAuthList: Array<Promise<any>>;
  initAuth?: any;
  selectStyle?: any;
  placeholder?: string;
  required?: boolean;
}

const Authority = (props: AuthorityProps) => {
  const { form, name, label, initAuth, getAuthList, selectStyle = {}, placeholder, required } = props;
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [oauthAuthList, setOauthAuthList] = useState<any>([]);
  const [authLoading, setAuthLoading] = useState(false);

  const setCurAuth = (sshList = sshAuthList, httpList = httpAuthList) => {
    // 设置初始值
    if (initAuth[SCM_MAP[initAuth.auth_type]]?.id) {
      form.setFieldsValue({ [name]: `${initAuth.auth_type}#${initAuth[SCM_MAP[initAuth.auth_type]]?.id}` });
    }

    // 确保当前凭证在select数据内
    if (
      initAuth.scm_ssh
      && initAuth.auth_type === AUTH_TYPE.SSH
      && !find(sshList, { id: initAuth.scm_ssh?.id })
    ) {
      setSshAuthList([initAuth.scm_ssh, ...sshList]);
    }
    if (
      initAuth.scm_account
      && initAuth.auth_type === AUTH_TYPE.HTTP
      && !find(httpList, { id: initAuth.scm_account?.id })
    ) {
      setHttpAuthList([initAuth.scm_account, ...httpList]);
    }
  };

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all(getAuthList).then((result: any) => {
      const activeOauth = filter(
        result[2].map((item: any) => ({
          ...item,
          platform_status: get(result[3], item.scm_platform_name, [false]),
        })),
        'platform_status',
      );
      setSshAuthList(result[0]);
      setHttpAuthList(result[1]);
      setOauthAuthList(activeOauth);
      setAuthLoading(false);
    });
  };

  useEffect(() => {
    getAuth();
  }, []);

  useEffect(() => {
    if (!isEmpty(initAuth) && !authLoading) {
      setCurAuth();
    }
  }, [initAuth, authLoading]);

  return (
    <Form.Item label={label} required={required}>
      <Form.Item name={name} noStyle rules={[{ required, message: '请选择仓库凭证' }]}>
        <Select
          style={selectStyle}
          placeholder={placeholder}
          getPopupContainer={() => document.body}
          optionLabelProp="label"
        >
          {!isEmpty(oauthAuthList) && (
            <OptGroup label={AUTH_TYPE_TXT.OAUTH}>
              {oauthAuthList.map((auth: any) => (
                <Option
                  key={`${AUTH_TYPE.OAUTH}#${auth.id}`}
                  value={`${AUTH_TYPE.OAUTH}#${auth.id}`}
                  label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${AUTH_TYPE_TXT.OAUTH}`}
                >
                  {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}
                </Option>
              ))}
            </OptGroup>
          )}
          {!isEmpty(sshAuthList) && (
            <OptGroup label={AUTH_TYPE_TXT.SSH}>
              {sshAuthList.map((auth: any) => (
                <Option
                  key={`${AUTH_TYPE.SSH}#${auth.id}`}
                  value={`${AUTH_TYPE.SSH}#${auth.id}`}
                  label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${auth.name}`}
                >
                  {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: {auth.name}
                  <small style={{ marginLeft: 8, color: '#8592a6' }}>(在 {auth.auth_origin} 创建)</small>
                </Option>
              ))}
            </OptGroup>
          )}
          {!isEmpty(httpAuthList) && (
            <OptGroup label={AUTH_TYPE_TXT.HTTP}>
              {httpAuthList.map((auth: any) => (
                <Option
                  key={`${AUTH_TYPE.HTTP}#${auth.id}`}
                  value={`${AUTH_TYPE.HTTP}#${auth.id}`}
                  label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${auth.scm_username}`}
                >
                  {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: {auth.scm_username}
                  <small style={{ marginLeft: 8, color: '#8592a6' }}>(在 {auth.auth_origin} 创建)</small>
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
          <Button type='link' className="ml-12" href='/user/auth' target='_blank'><PlusIcon /></Button>
        </Tooltip>
        <Tooltip title='刷新凭证' placement='top' getPopupContainer={() => document.body}>
          <Button
            type='text'
            className="ml-12"
            disabled={authLoading}
            onClick={getAuth}
          ><RefreshIcon /></Button>
        </Tooltip>
      </div>
    </Form.Item>
  );
};

export default Authority;
