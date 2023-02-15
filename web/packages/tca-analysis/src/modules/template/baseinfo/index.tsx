// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 基础属性
 */

import React, { useEffect, useState } from 'react';
import cn from 'classnames';

import {
  Form,
  Input,
  Select,
  Button,
  message,
} from 'coding-oa-uikit';

import { updateTmpl, syncScheme, getTmplLint, updateTmplLint } from '@src/services/template';
import NodeTag from '@src/components/node-tag';
import Copy from '@src/components/copy';

import SyncModal from '../sync-modal';
import style from './style.scss';
import formStyle from '../style.scss';

const { Option } = Select;
const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
};

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
  }, [tmplId]);

  useEffect(() => {
    form.resetFields();
  }, [tmplId, lintConfig.envs]);

  const onFinish = (formData: any) => {
    setVisible(true);
    setFormData(formData);
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
        className={cn(style.baseConfig, formStyle.schemeFormVertical)}
        initialValues={{ ...data, envs: lintConfig.envs }}
        form={form}
        onFinish={onFinish}
      >
         <Form.Item {...layout} name="id" label="模板ID">
          <span className={style.tooltip}>
            {data.id}
            <Copy text='点击复制方案模板ID' copyText={data.id}/>
          </span>
        </Form.Item>
        <Form.Item
          {...layout}
          name="name"
          label="模板名称"
          rules={[
            { required: true, message: '请输入模板名称' },
            { max: 127, message: '模板名称过长' },
          ]}
        >
          <Input readOnly={isSysTmpl} placeholder="请输入模板名称" />
        </Form.Item>
        <Form.Item {...layout} name="description" label="模板描述">
          <Input.TextArea readOnly={isSysTmpl} rows={3} placeholder="请输入模板描述" />
        </Form.Item>
        <Form.Item
          {...layout}
          name="languages"
          label="分析语言"
          rules={[{ required: true, message: '请选择分析语言' }]}
        >
          <Select disabled={isSysTmpl} mode="multiple" placeholder="请选择分析语言" optionFilterProp='children'>
            {languages.map(item => (
              <Option key={item.name} value={item.name}>
                {item.display_name}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <NodeTag
          {...layout}
          name="tag"
          label="运行环境"
          rules={[{ required: true, message: '请选择运行环境' }]}
          tags={tags}
          disabled={isSysTmpl}
        />
        <Form.Item {...layout} name="envs" label="环境变量">
          <Input.TextArea rows={3} placeholder="请输入环境变量" />
        </Form.Item>
        {
          !isSysTmpl && (
            <>
              <Form.Item style={{ marginTop: 30 }}>
                <Button type="primary" htmlType="submit" style={{ marginRight: 10 }}>
                  保存
                </Button>
                <Button onClick={() => form.resetFields()}>取消</Button>
              </Form.Item>
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
