// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案模板 - 权限配置
 */
import React, { useState, useEffect } from 'react';
import { uniqBy } from 'lodash';

import { Form, Button, message, Select, Switch, SubmitContext } from 'tdesign-react';
import FormLabelWithHelp from '@src/components/title-with-help';

import { getPermConf, updatePermConf } from '@src/services/template';
import { getOrgMembers } from '@src/services/common';
import { TMPL_SCHEME_PERM_OPEN_LABEL } from '@plat/modules';

import style from './style.scss';

const { FormItem } = Form;

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
  }, [orgSid]);

  useEffect(() => {
    getPermConf(orgSid, tmplId).then((response) => {
      setData(response);
      const formData = {
        ...response,
        execute_scope: response.execute_scope === 1,
        edit_managers_list: response.edit_managers?.map((item: any) => item.username),
        execute_managers_list: response.execute_managers?.map((item: any) => item.username),
      };
      form.setFieldsValue(formData);
    });
  }, [orgSid, tmplId, form]);

  const onFinish = (context: SubmitContext<FormData>) => {
    if (context.validateResult === true) {
      const formData = form.getFieldsValue(true);
      updatePermConf(orgSid, tmplId, {
        ...formData,
        execute_scope: formData.execute_scope ? 1 : 2, // 1 公开，2 私有
      }).then((response) => {
        message.success('更新成功');
        setData(response);
      });
    }
  };

  return (
    <Form
      labelAlign="left"
      className={style.permissionForm}
      form={form}
      initialData={{
        execute_scope: data.execute_scope === 1,
        edit_managers_list: data.edit_managers?.map((item: any) => item.username),
        execute_managers_list: data.execute_managers?.map((item: any) => item.username),
      }}
      resetType='initial'
      onSubmit={onFinish}
      labelWidth={160}
    >
      <FormItem
        label={TMPL_SCHEME_PERM_OPEN_LABEL}
        name="execute_scope"
      >
        <Switch />
      </FormItem>
      <FormItem
        name="edit_managers_list"
        label={<FormLabelWithHelp labelString='管理员' helpInfo='拥有模板编辑权限' />}
      >
        <Select
          showArrow
          multiple
          readonly={isSysTmpl}
          options={teamMembers.map((item: any) => ({
            label: item.nickname,
            value: item.username,
          }))}
          filterable
        />
      </FormItem>
      <FormItem
        name="execute_managers_list"
        label={<FormLabelWithHelp labelString='普通成员' helpInfo='可使用模板' />}
      >
        <Select
          showArrow
          multiple
          readonly={isSysTmpl}
          options={teamMembers.map((item: any) => ({
            label: item.nickname,
            value: item.username,
          }))}
          filterable
        />
      </FormItem>
      {!isSysTmpl && (
        <FormItem style={{ marginTop: 30 }}>
          <Button theme="primary" type="submit" style={{ marginRight: 10 }}>
            保存
          </Button>
          <Button theme='default' type='reset'>
            取消
          </Button>
        </FormItem>
      )}
    </Form>
  );
};

export default Permission;
