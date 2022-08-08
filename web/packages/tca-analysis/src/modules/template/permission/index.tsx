// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案模板 - 权限配置
 */
import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { uniqBy } from 'lodash';

import { Form, Tooltip, Button, message, Select, Switch } from 'coding-oa-uikit';
import QuestionCircle from 'coding-oa-uikit/lib/icon/QuestionCircle';

import { getPermConf, updatePermConf } from '@src/services/template';
import { getOrgMembers } from '@src/services/common';

import formStyle from '../style.scss';
import style from './style.scss';

const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
};

interface PermissionProps {
  orgSid: string;
  tmplId: number;
  isSysTmpl: boolean;
}

const Permission = (props: PermissionProps) => {
  const { orgSid, tmplId, isSysTmpl } = props;
  const [form] = Form.useForm();
  const [data, setData] = useState<any>({});
  const [teamMembers, setTeamMembers] = useState<any>([]);

  useEffect(() => {
    if (orgSid) {
      getOrgMembers(orgSid).then((res) => {
        const { admins = [], users = [] } = res;
        setTeamMembers(uniqBy([...admins, ...users], 'username'));
      });
    }
  }, []);

  useEffect(() => {
    getPermConf(orgSid, tmplId).then((response) => {
      setData(response);
      form.resetFields();
    });
  }, [tmplId]);

  const onFinish = (formData: any) => {
    updatePermConf(orgSid, tmplId, {
      ...formData,
      execute_scope: formData.execute_scope ? 1 : 2, // 1 公开，2 私有
    }).then((response) => {
      message.success('更新成功');
      setData(response);
      // form.resetFields();
    });
  };

  return (
    <Form
      labelAlign="left"
      className={cn(formStyle.schemeFormVertical, style.permissionForm)}
      form={form}
      initialValues={{
        execute_scope: data.execute_scope === 1,
        edit_managers_list: data.edit_managers?.map((item: any) => item.username),
        execute_managers_list: data.execute_managers?.map((item: any) => item.username),
      }}
      onFinish={onFinish}
    >
      <Form.Item
        {...layout}
        label="是否团队内公开"
        name="execute_scope"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      <Form.Item
        {...layout}
        name="edit_managers_list"
        label={
          <span>
            管理员
            <Tooltip
              getPopupContainer={() => document.getElementById('main-container')}
              title="拥有模板编辑权限"
            >
              <QuestionCircle className={formStyle.questionIcon} />
            </Tooltip>
          </span>
        }
      >
        <Select
          showSearch
          mode="multiple"
          disabled={isSysTmpl}
          optionFilterProp="label"
          getPopupContainer={() => document.getElementById('main-container')}
          options={teamMembers.map((item: any) => ({
            label: item.nickname,
            value: item.username,
          }))}
        />
      </Form.Item>

      <Form.Item
        {...layout}
        name="execute_managers_list"
        label={
          <span>
            普通成员
            <Tooltip
              getPopupContainer={() => document.getElementById('main-container')}
              title="可使用模板"
            >
              <QuestionCircle className={formStyle.questionIcon} />
            </Tooltip>
          </span>
        }
      >
        <Select
          showSearch
          mode="multiple"
          disabled={isSysTmpl}
          optionFilterProp="label"
          getPopupContainer={() => document.getElementById('main-container')}
          options={teamMembers.map((item: any) => ({
            label: item.nickname,
            value: item.username,
          }))}
        />
      </Form.Item>
      {!isSysTmpl && (
        <Form.Item style={{ marginTop: 30 }}>
          <Button type="primary" htmlType="submit" style={{ marginRight: 10 }}>
            保存
          </Button>
          <Button
            onClick={() => {
              form.resetFields();
            }}
          >
            取消
          </Button>
        </Form.Item>
      )}
    </Form>
  );
};

export default Permission;
