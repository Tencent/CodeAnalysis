import React, { useEffect, useState } from 'react';
import { isEmpty, get } from 'lodash';
import { Button, Form, Select, Tooltip, FormInstanceFunctions } from 'tdesign-react';
import { AddIcon, RefreshIcon } from 'tdesign-icons-react';

import { AuthTypeEnum, AuthTypeTxtEnum, SCM_PLATFORM_CHOICES, SCM_MAP } from '../constant';
import { UserAuthAPI } from '../types';
import { openURL } from '../../../util';

const { FormItem } = Form;

const { Option, OptionGroup } = Select;

const authInitData = {
  sshList: [],
  accountList: [],
  oauthList: [],
};

interface UserAuthFormItemProps {
  /** form 实例 */
  form: FormInstanceFunctions;
  /** form item name */
  name: string;
  /** form item label */
  label: string | React.ReactNode;
  /** form item required */
  required?: boolean;
  /** form item layout */
  formLayout?: any;
  /** select placeholder */
  placeholder?: string;
  /** select allowClear */
  allowClear?: boolean;
  /** select style */
  selectStyle?: React.CSSProperties;
  /** auth api */
  userAuthAPI: UserAuthAPI;
  /** 传入的 scm auth 信息 */
  authinfo?: any;
  /** 新增凭证路由 */
  addAuthRouter?: string;
}

const UserAuthFormItem = ({
  form, name, label, required, placeholder, allowClear, selectStyle,
  userAuthAPI, authinfo, addAuthRouter,
}: UserAuthFormItemProps) => {
  const [initAuthData, setInitAuthData] = useState<{
    accountList: any[], sshList: any[], oauthList: any[]
  }>(authInitData);
  const [authData, setAuthData] = useState<{ accountList: any[], sshList: any[], oauthList: any[] }>(authInitData);
  const [loading, setLoading] = useState(false);
  const [reload, setReload] = useState(false);

  useEffect(() => {
    // 获取凭证列表，记录记录当前用户个人凭证
    setLoading(true);
    userAuthAPI.getAuthInfos().then(setInitAuthData)
      .finally(() => setLoading(false));
  }, [reload]);

  useEffect(() => {
    // 判断是否存在authinfo，如果存在则配置auth列表，且setFieldsValue
    if (authinfo) {
      const { scm_oauth: scmOAuth, scm_ssh: scmSsh, scm_account: scmAccount, auth_type: authType } = authinfo;
      const { oauthList, sshList, accountList } = initAuthData;
      if (scmOAuth && authType === AuthTypeEnum.OAUTH && !oauthList.filter(i => i.id === scmOAuth.id).length) {
        setAuthData({ oauthList: [scmOAuth, ...oauthList], sshList, accountList });
      } else if (scmSsh && authType === AuthTypeEnum.SSH && !sshList.filter(i => i.id === scmSsh.id).length) {
        setAuthData({ oauthList, sshList: [scmSsh, ...sshList], accountList });
      } else if (scmAccount && authType === AuthTypeEnum.HTTP
        && !accountList.filter(i => i.id === scmAccount.id).length) {
        setAuthData({ oauthList, sshList, accountList: [scmAccount, ...accountList] });
      } else {
        setAuthData(initAuthData);
      }
      const auth = authinfo?.[SCM_MAP[authinfo.auth_type as AuthTypeEnum]];
      if (auth?.id) {
        form?.setFieldsValue?.({ [name]: `${authinfo.auth_type}#${auth.id}` });
      }
    } else {
      // 默认配置auth列表
      form?.setFieldsValue?.({ [name]: undefined });
      setAuthData(initAuthData);
    }
  }, [authinfo, form, name, initAuthData]);

  return <FormItem label={label}>
    <FormItem name={name} rules={[{ required, message: '请选择仓库凭证' }]}>
      <Select
        style={selectStyle}
        placeholder={placeholder}
        clearable={allowClear}
      >
        {/* oauth */}
        {!isEmpty(authData.oauthList) && (
          <OptionGroup label={AuthTypeTxtEnum.OAUTH}>
            {authData.oauthList.map((auth: any) => (
              <Option
                key={`${AuthTypeEnum.OAUTH}#${auth.id}`}
                value={`${AuthTypeEnum.OAUTH}#${auth.id}`}
                label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${auth.user?.username || auth.user}`}
              >
                {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: {auth.user?.username || auth.user}
                <small style={{ marginLeft: 8, color: '#8592a6' }}>(在 {auth.auth_origin} 创建)</small>
              </Option>
            ))}
          </OptionGroup>
        )}
        {/* ssh */}
        {!isEmpty(authData.sshList) && (
          <OptionGroup label={AuthTypeTxtEnum.SSH}>
            {authData.sshList.map((auth: any) => (
              <Option
                key={`${AuthTypeEnum.SSH}#${auth.id}`}
                value={`${AuthTypeEnum.SSH}#${auth.id}`}
                label={`${get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: ${auth.name}`}
              >
                {get(SCM_PLATFORM_CHOICES, auth.scm_platform)}: {auth.name}
                <small style={{ marginLeft: 8, color: '#8592a6' }}>(在 {auth.auth_origin} 创建)</small>
              </Option>
            ))}
          </OptionGroup>
        )}
        {/* http */}
        {!isEmpty(authData.accountList) && (
          <OptionGroup label={AuthTypeTxtEnum.HTTP}>
            {authData.accountList.map((auth: any) => (
              <Option
                key={`${AuthTypeEnum.HTTP}#${auth.id}`}
                value={`${AuthTypeEnum.HTTP}#${auth.id}`}
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
        <Button variant='text' shape="circle" theme="primary"
          onClick={() => {
            openURL(addAuthRouter || '/user/auth');
          }}><AddIcon /></Button>
      </Tooltip>
      <Tooltip content='刷新凭证' placement='top'>
        <Button
          variant='text'
          shape="circle"
          loading={loading}
          onClick={() => {
            setReload(!reload);
          }}
        ><RefreshIcon /></Button>
      </Tooltip>
    </div>
  </FormItem>;
};

export default UserAuthFormItem;
