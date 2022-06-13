// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 仓库登记入口文件
 */
import React, { useState, useEffect } from 'react';
import { find, isEmpty, get, filter } from 'lodash';
import { Button, Form, Select, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';

// 项目内
import { t } from '@src/i18n/i18next';
import { SCM_PLATFORM } from '@src/common/constants';
import { AUTH_TYPE, AUTH_TYPE_TXT } from '@src/modules/repos/constants';
import { getPCAuthRouter } from '@src/modules/repos/routes';
import { getSSHInfo, getScmAccounts, putRepoAuth, getOAuthInfo, getPlatformStatus } from '@src/services/repos';

const { Option, OptGroup } = Select;

interface IProps {
  curRepo: any;
  repoId: number;
  orgSid: string;
  teamName: string;
}

const layout = {
  labelCol: { span: 3 },
};

/**
 * Todo: 目前仅存在http凭证，后续可能会添加各个oauth以及ssh等，后续再重新做其余认证模式处理
 */
const Authority = ({ curRepo, orgSid, teamName, repoId }: IProps) => {
  const [selectedAuth, setSelectedAuth] = useState<any>({});
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [oauthAuthList, setOauthAuthList] = useState<any>([]);
  // const [allAuthList, setAllAuthList] = useState<Array<any>>([]);
  const [authLoading, setAuthLoading] = useState(false);

  const scmAuth: any = curRepo?.scm_auth ?? {};
  let curAuth: any = {};
  if (scmAuth.auth_type) {
    switch (scmAuth?.auth_type) {
      case AUTH_TYPE.HTTP:
        curAuth = scmAuth.scm_account;
        break;
      case AUTH_TYPE.SSH:
        curAuth = scmAuth.scm_ssh;
        break;
      case AUTH_TYPE.OAUTH:
        curAuth = scmAuth.scm_oauth;
        break;
    }
    curAuth.auth_type = curRepo.scm_auth.auth_type;
  }

  const setCurAuth = (sshList = sshAuthList, httpList = httpAuthList, oauthList = oauthAuthList) => {
    // 确保当前凭证在select数据内
    if (
      curAuth.id
      && curAuth.auth_type === AUTH_TYPE.SSH
      && !find(sshList, { id: curAuth.id })
    ) {
      setSshAuthList([curAuth, ...sshList]);
    }
    if (
      curAuth.id
      && curAuth.auth_type === AUTH_TYPE.HTTP
      && !find(httpList, { id: curAuth.id })
    ) {
      setHttpAuthList([curAuth, ...httpList]);
    }
    if (
      curAuth.id
      && curAuth.auth_type === AUTH_TYPE.OAUTH
      && !find(oauthList, { id: curAuth.id })
    ) {
      setOauthAuthList([curAuth, ...oauthList]);
    }
  };

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      getScmAccounts().then(r => r.results || []),
      getOAuthInfo().then(r => r.results || []),
      getPlatformStatus().then(r => r || []),
    ]).then((result) => {
      const activeOauth = filter(
        result[2].map((item:any)=>({ 
          ...item, 
          platform_status: get(result[3], item.scm_platform_name, [false]),
        })),
        'platform_status'
      );
      setSshAuthList(result[0]);
      setHttpAuthList(result[1]);
      setOauthAuthList(activeOauth);
      setCurAuth(result[0], result[1], result[2]);
      setAuthLoading(false);
    });
  };

  const onFinish = () => {
    if (selectedAuth) {
      if (selectedAuth.id === curAuth.id) {
        message.info('认证未发生变更');
      } else {
        const scmAuth: any = {
          auth_type: selectedAuth.auth_type,
          scm_auth: null,
        };

        if (selectedAuth.auth_type === AUTH_TYPE.HTTP) {
          scmAuth.scm_account = selectedAuth.id;
          scmAuth.scm_ssh = null;
          scmAuth.scm_oauth = null;
        }

        if (selectedAuth.auth_type === AUTH_TYPE.SSH) {
          scmAuth.scm_ssh = selectedAuth.id;
          scmAuth.scm_account = null;
          scmAuth.scm_oauth = null;
        }

        if (selectedAuth.auth_type === AUTH_TYPE.OAUTH) {
          scmAuth.scm_oauth = selectedAuth.id;
          scmAuth.scm_account = null;
          scmAuth.scm_ssh = null;
        }

        putRepoAuth(orgSid, teamName, repoId, { scm_auth: scmAuth }).then(() => {
          message.success('已切换认证方式');
        });
      }
    } else {
      message.warning(t('请选择一条凭证用于代码库认证'));
    }
  };

  const onReset = () => {
    setSelectedAuth(curAuth.id
      ? {
        id: curAuth.id,
        auth_type: curAuth.auth_type,
      }
      : {});
  };

  useEffect(() => {
    getAuth();
  }, []);

  useEffect(() => {
    setSelectedAuth(curAuth.id
      ? {
        id: curAuth.id,
        auth_type: curAuth.auth_type,
      }
      : {});
    setCurAuth();
  }, [curRepo.id, curAuth.id]);

  return (
    <Form
      {...layout}
      name="authority"
      style={{ marginTop: '30px', width: '600px' }}
      onFinish={onFinish}
    >
      <Form.Item label={t('认证')} name="auth_id">
        <>
          <Select
            style={{ width: 300 }}
            value={
              selectedAuth.id
                ? `${selectedAuth.auth_type}#${selectedAuth.id}`
                : undefined
            }
            onChange={(value) => {
              setSelectedAuth({
                id: value.split('#')[1],
                auth_type: value.split('#')[0],
              });
            }}
            getPopupContainer={() => document.body}
          >
            {!isEmpty(oauthAuthList) && (
              <OptGroup label={AUTH_TYPE_TXT.OAUTH}>
                {oauthAuthList.map((auth: any) => (
                  <Option
                    key={`${AUTH_TYPE.OAUTH}#${auth.id}`}
                    value={`${AUTH_TYPE.OAUTH}#${auth.id}`}
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
                    key={`${AUTH_TYPE.SSH}#${auth.id}`}
                    value={`${AUTH_TYPE.SSH}#${auth.id}`}
                  >
                    {get(SCM_PLATFORM, auth.scm_platform, '其他')}：{auth.name}
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
                  >
                    {get(SCM_PLATFORM, auth.scm_platform, '其他')}：{auth.scm_username}
                  </Option>
                ))}
              </OptGroup>
            )}
          </Select>
          <Button
            className="ml-12"
            icon={<PlusIcon />}
            type="link"
            target="_blank"
            href={getPCAuthRouter()}
          >
            {t('新增凭证')}
          </Button>
          <Button
            className="ml-12"
            type="text"
            icon={<RefreshIcon />}
            loading={authLoading}
            onClick={() => getAuth()}
          >
            {t('重新拉取凭证')}
          </Button>
        </>
      </Form.Item>
      <div style={{ marginTop: '30px' }}>
        <Button type="primary" htmlType="submit" key="submit">
          {t('确定')}
        </Button>
        <Button className=" ml-12" htmlType="button" onClick={onReset}>
          {t('取消')}
        </Button>
      </div>
    </Form>
  );
};

export default Authority;
