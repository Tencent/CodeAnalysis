// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Form, Button, Input, message } from 'coding-oa-uikit';
import { pick } from 'lodash';

// 项目内
import { t } from '@src/i18n/i18next';
import { formatDateTime, getUserName } from '@src/utils';
import { getProjectTeam, putProjectTeam } from '@src/services/common';

const layout = {
  labelCol: { span: 6 },
};

const Overview = () => {
  const [form] = Form.useForm();
  const [team, setTeam] = useState<any>({});
  const [edit, setEdit] = useState(false);
  const { org_sid: orgSid, team_name: teamName }: any = useParams();

  // 重置
  const onReset = () => {
    setEdit(false);
    form.resetFields();
  };

  const onFinish = (values: any) => {
    putProjectTeam(
      orgSid,
      team.name,
      pick(values, ['name', 'display_name', 'description']),
    ).then((response: any) => {
      message.success(t('项目信息更新成功'));
      setTeam(response);
      onReset();
    });
  };

  const init = () => {
    getProjectTeam(orgSid, teamName).then((res) => {
      setTeam(res);
      onReset();
    });
  };

  useEffect(() => {
    if (teamName) {
      init();
    }
  }, [orgSid, teamName]);

  return (
    <div className="pa-lg">
      <h3 className="mb-md">{t('项目概览')}</h3>
      <Form
        {...layout}
        style={{ width: '530px' }}
        form={form}
        initialValues={team}
        onFinish={values => onFinish(values)}
      >
        <Form.Item label={t('项目唯一标识')} name="name">
          <span>{team.name}</span>
        </Form.Item>
        <Form.Item
          label={t('项目名称')}
          name="display_name"
          rules={edit ? [{ required: true, message: t('项目名称为必填项') }] : undefined}
        >
          {edit ? <Input width={400} /> : <>{team.display_name}</>}
        </Form.Item>
        <Form.Item label={t('项目描述')} name="description">
          {edit ? <Input.TextArea /> : <>{team.description}</>}
        </Form.Item>

        <Form.Item label={t('创建人')} name="creator">
          <span>{getUserName(team.creator)}</span>
        </Form.Item>
        <Form.Item label={t('创建时间')} name="created_time">
          <span>{formatDateTime(team.created_time)}</span>
        </Form.Item>
        <div style={{ marginTop: '30px' }}>
          {edit ? (
            <>
              <Button type="primary" htmlType="submit" key="submit">
                {t('确定')}
              </Button>
              <Button className=" ml-12" htmlType="button" onClick={onReset}>
                {t('取消')}
              </Button>
            </>
          ) : (
            <Button
              key="edit"
              htmlType="button"
              type="primary"
              onClick={() => setEdit(true)}
            >
              {t('编辑')}
            </Button>
          )}
        </div>
      </Form>
    </div>
  );
};

export default Overview;
