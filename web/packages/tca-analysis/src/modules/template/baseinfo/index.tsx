// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 基础属性
 */

import React, { useEffect, useState } from 'react';

import {
  Form,
  Button,
  message,
  SubmitContext,
} from 'tdesign-react';

import { updateTmpl, syncScheme, getTmplLint, updateTmplLint } from '@src/services/template';
import Copy from '@src/components/copy';

import BaseConfigForm from '@src/components/schemes/base-config-form';
import SyncModal from '../sync-modal';
import style from './style.scss';

const { FormItem } = Form;

interface BaseConfigProps {
  orgSid: string;
  isSysTmpl: boolean;
  tmplId: number;
  tags: any[];
  languages: any[];
  data: any;
  callback?: (data: any) => void;
}

const BaseConfig = (props: BaseConfigProps) => {
  const { orgSid, isSysTmpl, data, tmplId, tags, languages, callback } = props;
  const [form] = Form.useForm();
  const [visible, setVisible] = useState(false);
  const [formData, setFormData] = useState<any>({});
  const [lintConfig, setLintConfig] = useState<any>({});

  useEffect(() => {
    if (tmplId) {
      getTmplLint(orgSid, tmplId).then(res => setLintConfig(res));
    }
  }, [tmplId, orgSid]);

  const onFinish = (context: SubmitContext<FormData>) => {
    if (context.validateResult === true) {
      const data = form.getFieldsValue(true);
      setVisible(true);
      setFormData(data);
    }
  };

  const onSync = (keys: any) => {
    if (formData.envs !== lintConfig.envs) {
      updateTmplLint(orgSid, tmplId, {
        ...lintConfig,
        envs: formData.envs,
      }).then((res) => {
        setLintConfig(res);
      });
    }
    updateTmpl(orgSid, tmplId, { ...data, ...formData }).then((response: any) => {
      callback?.(response);
      if (keys.length === 0) {
        setVisible(false);
        message.success('更新成功');
      }
    });

    if (keys.length > 0) {
      syncScheme(orgSid, tmplId, {
        sync_basic_conf: true,
        sync_lint_build_conf: true,
        schemes: keys,
      }).then(() => {
        message.success('同步成功');
        setVisible(false);
      });
    }
  };

  return (
    <>
      <Form
        labelAlign="left"
        className={style.baseConfig}
        form={form}
        initialData={{ ...data, envs: lintConfig.envs }}
        onSubmit={onFinish}
        labelWidth={180}
        resetType='initial'
      >
        <FormItem name="id" label="模板ID">
          <span className={style.tooltip}>
            {data.id}
            <Copy text='点击复制方案模板ID' copyText={data.id}/>
          </span>
        </FormItem>
        <BaseConfigForm
          name='模板'
          readonly={isSysTmpl}
          tags={tags}
          languages={languages}
          data={data}
        />
        {
          !isSysTmpl && (
            <>
              <FormItem style={{ marginTop: 30 }}>
                <Button theme="primary" type="submit" style={{ marginRight: 10 }}>
                  保存
                </Button>
                <Button type='reset' theme='default'>取消</Button>
              </FormItem>
            </>
          )
        }

      </Form>
      {
        !isSysTmpl && (
          <SyncModal
            tmplId={tmplId}
            visible={visible}
            onClose={() => setVisible(false)}
            onOk={onSync}
          />
        )
      }
    </>
  );
};

export default BaseConfig;
