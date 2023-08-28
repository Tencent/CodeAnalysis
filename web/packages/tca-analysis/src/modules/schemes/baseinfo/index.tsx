// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 基础属性
 */

import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import {
  Form,
  Button,
  Dropdown,
  message,
  Dialog,
  SubmitContext,
} from 'tdesign-react';
import { EllipsisIcon } from 'tdesign-icons-react';

import { updateSchemeBasic, updateLintConfig } from '@src/services/schemes';
import BaseConfigForm from '@src/components/schemes/base-config-form';

import style from './style.scss';
import formStyle from '../style.scss';

const { FormItem } = Form;

interface BaseConfigProps {
  orgSid: string;
  teamName: string;
  repoId: string | number;
  tags: any[];
  languages: any[];
  data: any;
  lintConf: any;   // 环境变量初始值
  callback?: (data: any) => void;
}

const BaseConfig = (props: BaseConfigProps) => {
  const { orgSid, teamName, data, repoId, tags, languages, lintConf, callback } = props;
  const [form] = Form.useForm();
  const [visible, setVisible] = useState(false);
  const [isDefault, setDefault] = useState(true);
  const schemeId = data.id;

  useEffect(() => form.setFieldsValue({ ...data, envs: lintConf.envs }), [schemeId, lintConf]);

  // todo: remove
  const openModal = ({ value }: { value: string }) => {
    if (value === 'restore') {
      onFinish({ ...data, status: 1 });
    } else {
      setVisible(true);
      setDefault(value === 'default');
    }
  };
  const onFinish = (formData: any) => {
    updateSchemeBasic(orgSid, teamName, repoId, schemeId, { ...data, ...formData }).then((response: any) => {
      message.success('更新成功');
      callback?.(response);
    });

    if (formData.envs !== lintConf.envs) {
      updateLintConfig(orgSid, teamName, repoId, schemeId, {
        ...lintConf,
        envs: formData.envs,
      });
    }
  };

  const onSubmitHandle = (context: SubmitContext<FormData>) => {
    if (context.validateResult === true) {
      const formData = form.getFieldsValue(true);
      onFinish(formData);
    }
  };


  const setSchemeStatus = () => {
    const updateData = data;

    if (isDefault) {
      updateData.default_flag = true;
    } else {
      updateData.status = 2;
    }

    onFinish(updateData);
    setVisible(false);
  };

  const options = data.status === 2 ? [
    {
      value: 'restore',
      content: '恢复方案',
    },
  ] : [
    {
      value: 'default',
      content: '设为默认方案',
      disabled: data.default_flag,
    },
    {
      value: 'deprecated',
      content: '废弃方案',
      disabled: data.default_flag,
      theme: 'error',
    },
  ];

  return (
    <>
      <Form
        labelAlign="left"
        className={cn(style.baseConfig, formStyle.schemeFormVertical)}
        initialData={{ ...data, envs: lintConf.envs }}
        form={form}
        onSubmit={onSubmitHandle}
        labelWidth={180}
        resetType='initial'
      >
        <BaseConfigForm
          name='方案'
          tags={tags}
          languages={languages}
          data={data}
        />
        <FormItem style={{ marginTop: 30 }}>
          <Button theme="primary" type="submit" style={{ marginRight: 10 }}>
            保存
          </Button>
          <Button type='reset' theme='default'>取消</Button>
          <Dropdown
            options={options}
            onClick={openModal}
          >
            <Button className={formStyle.ellipsis} variant='text' icon={<EllipsisIcon />} />
          </Dropdown>
        </FormItem>
      </Form>

      <Dialog
        visible={visible}
        className={style.baseModal}
        onCancel={() => setVisible(false)}
        confirmBtn={<Button theme={isDefault ? 'primary' : 'danger'} onClick={setSchemeStatus}>确认</Button>}
        onConfirm={setSchemeStatus}
        header={isDefault ? '设为默认方案' : '废弃方案'}
      >
        <p>
          {isDefault
            ? '建议默认分析方案用于主干代码分析，请谨慎操作！'
            : '废弃该方案将导致关联的分析项目关闭，确定要废弃该方案？请查看关联分支列表，慎重操作！'}
        </p>
      </Dialog>
    </>
  );
};

export default BaseConfig;
