// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router-dom';
import { Form, Select, Input, Button, message } from 'coding-oa-uikit';
// Radio
import { get, isEmpty } from 'lodash';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import RefreshIcon from 'coding-oa-uikit/lib/icon/Refresh';

// 项目内
import { useStateStore, useDispatchStore } from '@src/context/store';
import { SCM_PLATFORM } from '@src/common/constants';
import { SET_CUR_REPO, SET_REPOS } from '@src/context/constant';
import { getScmAccounts, postRepo, getSSHInfo } from '@src/services/repos';
import { t } from '@src/i18n/i18next';
import { getPCAuthRouter, getRepoRouter } from '@src/modules/repos/routes';
import { AUTH_TYPE, AUTH_TYPE_TXT, REPO_TYPE, REPO_TYPE_OPTIONS } from './constants';
import s from './style.scss';

const { Option, OptGroup } = Select;

// TODO: 暂时不做组织处理
// const REPO_ORG_TYPE = {
//     PERSONAL: 1,
//     ORG: 2,
// };

// const REPO_ORG_TYPE_OPTIONS = [
//     {
//         label: t('个人'),
//         value: REPO_ORG_TYPE.PERSONAL,
//     },
//     {
//         label: t('组织'),
//         value: REPO_ORG_TYPE.ORG,
//     },
// ];

const layout = {
  labelCol: { span: 3 },
};

const Create = () => {
  const [form] = Form.useForm();
  const history = useHistory();
  const { repos } = useStateStore();
  const dispatch = useDispatchStore();

  const { org_sid: orgSid, team_name: teamName }: any = useParams();
  // const [allAuthList, setAllAuthList] = useState<Array<any>>([]);
  const [sshAuthList, setSshAuthList] = useState<any>([]);
  const [httpAuthList, setHttpAuthList] = useState<any>([]);
  const [submitLoading, setSubmitLoading] = useState(false);
  const [reload, setReload] = useState(false);
  const [authLoading, setAuthLoading] = useState(false);

  useEffect(() => {
    getAuth();
  }, [reload]);

  const getAuth = () => {
    setAuthLoading(true);
    Promise.all([
      getSSHInfo().then(r => r.results || []),
      getScmAccounts().then(r => r.results || []),
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

  const onFinish = (values: any) => {
    const { name, scm_auth_id: scmAuthId, address, symbol } = values;
    const [authType, id] = scmAuthId?.split('#') ?? [];
    const data = {
      name,
      create_from: 'codedog_web',
      repo_type: values.repo_type,
      scm_auth: {
        auth_type: authType,
      },
      ...address,
    };

    if (data.scm_auth.auth_type === AUTH_TYPE.HTTP) {
      data.scm_auth.scm_account = id;
    } else {
      data.scm_auth.scm_ssh = id;
    }

    if (symbol) {
      data.symbol = symbol;
    }
    setSubmitLoading(true);
    postRepo(orgSid, teamName, data)
      .then((response) => {
        message.success(t('登记代码库成功'));
        history.replace(getRepoRouter(orgSid, teamName, response.id));
        dispatch({
          type: SET_REPOS,
          payload: [...repos, response],
        });
        dispatch({
          type: SET_CUR_REPO,
          payload: response,
        });
      })
      .finally(() => {
        setSubmitLoading(false);
      });
  };

  const onReset = () => {
    form.resetFields();
  };

  const initialValues = {
    address: {
      scm_type: REPO_TYPE.GIT,
    },
    // repo_type: REPO_ORG_TYPE.PERSONAL,
  };

  /**
     * 仓库别名获取焦点时将代码库地址后缀赋予仓库别名
     */
  const onRepoNameFocus = () => {
    const address = form.getFieldValue('address');
    const scmUrl = get(address, 'scm_url', null);
    if (scmUrl) {
      const name = scmUrl.split('/');
      form.setFieldsValue({
        name: name[name.length - 1],
      });
    }
  };

  return (
    <div className={s.repoCreateContainer}>
      <div className={s.tit}>{t('代码库登记')}</div>
      <Form
        {...layout}
        name="repo-create"
        form={form}
        onFinish={onFinish}
        initialValues={initialValues}
        style={{ width: '820px' }}
      >
        {/* <Form.Item required label={t('仓库所属')} name="repo_type" >
                    <Radio.Group>
                        {REPO_ORG_TYPE_OPTIONS.map(item => (
                            <Radio.Button key={item.value} value={item.value}>
                                {item.label}
                            </Radio.Button>
                        ))}
                    </Radio.Group>
                </Form.Item> */}

        <Form.Item required label={t('仓库地址')}>
          <Input.Group compact>
            <Form.Item name={['address', 'scm_type']} noStyle>
              <Select style={{ width: 70 }}>
                {REPO_TYPE_OPTIONS.map((item: string, index) => (
                  <Option key={index} value={item}>
                    {item.toUpperCase()}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item
              name={['address', 'scm_url']}
              noStyle
              rules={[
                { required: true, message: t('请输入代码库地址') },
                // {
                //     pattern: /(https?):\/\/[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]/,
                //     message: t('请输入合法的代码库地址'),
                // },
              ]}
            >
              <Input style={{ width: 430 }} />
            </Form.Item>
            <p className={s.formDesc}>
              由于境外代码托管平台可能存在网络问题，建议使用境内托管平台的代码库
            </p>
          </Input.Group>
        </Form.Item>
        <Form.Item
          name="name"
          label={t('仓库别名')}
          rules={[{ required: true, message: t('请输入代码库别名') }]}
        >
          <Input style={{ width: 500 }} onFocus={onRepoNameFocus} />
        </Form.Item>
        <Form.Item label={t('认证')} required>
          <Form.Item
            name="scm_auth_id"
            style={{
              display: 'inline-block',
              marginBottom: 0,
              width: '500px',
            }}
            rules={[{ required: true, message: t('请选择一项仓库认证方式') }]}
          >
            <Select style={{ width: 500 }} getPopupContainer={() => document.body}>
              {!isEmpty(sshAuthList) && (
                <OptGroup label={AUTH_TYPE_TXT.SSH}>
                  {sshAuthList.map((auth: any) => (
                    <Option
                      key={auth.authId}
                      value={auth.authId}
                      auth_type={AUTH_TYPE.SSH}
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
                      key={auth.authId}
                      value={auth.authId}
                      auth_type={AUTH_TYPE.HTTP}
                    >
                      {get(SCM_PLATFORM, auth.scm_platform, '其他')}：{auth.scm_username}
                    </Option>
                  ))}
                </OptGroup>
              )}
            </Select>
          </Form.Item>
          <Button
            className="ml-12 mt-xs"
            type="link"
            target="_blank"
            href={getPCAuthRouter()}
            icon={<PlusIcon />}
          >
            {t('新增凭证')}
          </Button>
          <Button
            className="ml-12 mt-xs"
            type="text"
            icon={<RefreshIcon />}
            loading={authLoading}
            onClick={() => setReload(reload => !reload)}
          >
            {t('重新拉取凭证')}
          </Button>
        </Form.Item>
        <div style={{ marginTop: '30px' }}>
          <Button type="primary" htmlType="submit" key="submit" loading={submitLoading}>
            {t('确定')}
          </Button>
          <Button className=" ml-12" htmlType="button" onClick={onReset}>
            {t('取消')}
          </Button>
          <Button
            className=" ml-12"
            htmlType="button"
            type="text"
            onClick={() => history.goBack()}
          >
            {t('返回')}
          </Button>
        </div>
      </Form>
    </div>
  );
};

export default Create;
