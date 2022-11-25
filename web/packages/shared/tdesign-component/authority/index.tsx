/**
 * 选择认证
 */
import React, { useState, useEffect } from 'react';
import { find, isEmpty, filter, get } from 'lodash';
import { useHistory } from 'react-router-dom';
import { Button, Form, Select, Tooltip, FormInstanceFunctions } from 'tdesign-react';
import { AddIcon, RefreshIcon } from 'tdesign-icons-react';

import { AUTH_TYPE, AUTH_TYPE_TXT, SCM_MAP, SCM_PLATFORM_CHOICES } from './constants';

const { FormItem } = Form;

const { Option, OptionGroup } = Select;

export interface RestfulListAPIParams {
  results: any[];
  count: number;
  next: string;
  previous: string
}

interface AuthorityProps {
  name: string; // 对应表单 name
  form: FormInstanceFunctions; // form 对象
  label: string | React.ReactNode; // FormItem label
  /* 接口顺序：获取ssh凭证，获取用户名密码凭证，获取各平台OAuth授权状态，获取各平台OAuth应用配置状态 **/
  getAuthList: Array<(param?: any) => Promise<any>>;
  initAuth?: any;
  selectStyle?: any;
  placeholder?: string;
  required?: boolean;
  allowClear?: boolean;
}

const Authority = (props: AuthorityProps) => {
  const { form, name, label, initAuth, getAuthList, selectStyle = {}, placeholder, required, allowClear } = props;
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [oauthAuthList, setOauthAuthList] = useState<any>([]);
  const [authLoading, setAuthLoading] = useState(false);
  const history = useHistory();

  const setCurAuth = (sshList = sshAuthList, httpList = httpAuthList, oauthList = oauthAuthList) => {
    // 设置初始值
    if (initAuth[SCM_MAP[initAuth.auth_type]]?.id) {
      form?.setFieldsValue?.({ [name]: `${initAuth.auth_type}#${initAuth[SCM_MAP[initAuth.auth_type]]?.id}` });
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
    if (
      initAuth.scm_oauth
      && initAuth.auth_type === AUTH_TYPE.OAUTH
      && !find(oauthAuthList, { id: initAuth.scm_oauth?.id })
    ) {
      setOauthAuthList([initAuth.scm_oauth, ...oauthList]);
    }
  };

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all([
      getAuthList[0]({ limit: 200 })
        .then(({ results }: RestfulListAPIParams) => results || []),
      getAuthList[1]({ limit: 200 })
        .then(({ results }: RestfulListAPIParams) => results || []),
      getAuthList[2]()
        .then(({ results }: RestfulListAPIParams) => results || []),
      getAuthList[3]().then(r => r || {}),
    ]).then((result: any) => {
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
    <FormItem label={label} >
      <FormItem name={name} rules={[{ required, message: '请选择仓库凭证' }]}>
        <Select
          style={selectStyle}
          placeholder={placeholder}
          clearable={allowClear}
        >
          {!isEmpty(oauthAuthList) && (
            <OptionGroup label={AUTH_TYPE_TXT.OAUTH}>
              {oauthAuthList.map((auth: any) => (
                <Option
                  key={`${AUTH_TYPE.OAUTH}#${auth.id}`}
                  value={`${AUTH_TYPE.OAUTH}#${auth.id}`}
                  label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${auth.user?.username || auth.user}`}
                >
                  {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: {auth.user?.username || auth.user}
                  <small style={{ marginLeft: 8, color: '#8592a6' }}>(在 {auth.auth_origin} 创建)</small>
                </Option>
              ))}
            </OptionGroup>
          )}
          {!isEmpty(sshAuthList) && (
            <OptionGroup label={AUTH_TYPE_TXT.SSH}>
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
            </OptionGroup>
          )}
          {!isEmpty(httpAuthList) && (
            <OptionGroup label={AUTH_TYPE_TXT.HTTP}>
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
            </OptionGroup>
          )}
        </Select>
      </FormItem>
      <div style={{
        position: 'absolute',
        top: 0,
        right: 0,
      }}>
        <Tooltip content='新增凭证' placement='top'>
          <Button variant='text' shape="circle" theme="primary" onClick={() => history.push('/user/auth')}><AddIcon /></Button>
        </Tooltip>
        <Tooltip content='刷新凭证' placement='top'>
          <Button
            variant='text'
            shape="circle"
            loading={authLoading}
            onClick={getAuth}
          ><RefreshIcon /></Button>
        </Tooltip>
      </div>
    </FormItem>
  );
};

export default Authority;
