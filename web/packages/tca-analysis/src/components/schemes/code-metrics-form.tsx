// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 分析方案 - 代码度量
 */
import React, { useEffect } from 'react';
import { forEach } from 'lodash';

import { Form, InputNumber, Switch, Button, SubmitContext } from 'tdesign-react';

import FormLabelWithHelp from '@src/components/title-with-help';
import style from './style.scss';

const { FormItem } = Form;

interface CodeMetricsFormProps {
  readonly?: boolean;
  data: any;
  onSubmitHandle: (formData: any) => void;
  update: (formData: any, info: string, callback?: any) => void;
}

const CodeMetricsForm = ({
  readonly = false,
  data,
  onSubmitHandle,
  update,
}: CodeMetricsFormProps) => {
  const [form] = Form.useForm();

  useEffect(() => {
    form.setFieldsValue(data);
  }, [data, form]);

  const onFinish = (context: SubmitContext<FormData>) => {
    if (context.validateResult === true) {
      const submitData = form.getFieldsValue(true);
      // 处理InputNumber置空时值为''导致的兼容性问题
      forEach(submitData, (value: string | number, key: string) => {
        if (value === '') {
          submitData[key] = null;
        }
      });
      onSubmitHandle(submitData);
    }
  };

  return (
    <Form
      labelAlign="left"
      className={style.codeMetrics}
      initialData={data}
      form={form}
      resetType='initial'
      onSubmit={onFinish}
    >
      <FormLabelWithHelp
        size='large'
        labelString='圈复杂度'
        helpInfo='可以发现执行路径较多的方法，降低代码的圈复杂度，可测性更高。支持C、C++、Java、C#、JavaScript、Python、Objective-C、Ruby、PHP、Swift、Scala、Go、Lua共13种语言'
      />
      <FormItem label='是否启用' name="cc_scan_enabled">
        <Switch
          size='small'
          disabled={readonly}
          onChange={(checked: boolean) => update({
            cc_scan_enabled: checked,
          }, `圈复杂度${checked ? '开启' : '关闭'}`)}
        />
      </FormItem>
      {
        data.cc_scan_enabled && (
          <FormItem
            name='min_ccn'
            // label='检测阈值'
            label={
              <FormLabelWithHelp
                labelString='检测阈值'
                helpInfo='仅上报圈复杂度超过该阈值的方法，默认20'
              />
            }
          >
            <InputNumber readonly={readonly} theme="normal" placeholder='默认20' style={{ width: 130 }} />
          </FormItem>
        )
      }
      <FormLabelWithHelp
        size='large'
        labelString='重复代码'
        helpInfo='可以发现重复的代码，避免重复代码可以让代码更简洁，更易维护。支持C、C++、Java、JavaScript、Objective-C、PHP、Python、C#、Ruby、Kotlin、Go、Lua、Swift、Scala共14种语言'
      />
      <FormItem label='是否启用' name='dup_scan_enabled'>
        <Switch
          disabled={readonly}
          size='small'
          onChange={(checked: boolean) => update({
            dup_scan_enabled: checked,
          }, `重复代码${checked ? '开启' : '关闭'}`)}
        />
      </FormItem>
      {
        data.dup_scan_enabled && (
          <>
            <FormItem
              className={style.intervalWrapper}
              label={
                <FormLabelWithHelp
                  labelString='长度区间'
                  helpInfo='一个单词（变量或操作符）记为'
                />
              }
            >
              <FormItem name='dup_block_length_min' className={style.interval}>
                <InputNumber
                  readonly={readonly}
                  theme="normal"
                  placeholder='最小默认120'
                />
              </FormItem>
              <span className={style.splitLine} />
              <FormItem name='dup_block_length_max' className={style.interval}>
                <InputNumber
                  readonly={readonly}
                  theme="normal"
                  placeholder='为空默认无限大'
                />
              </FormItem>
            </FormItem>
            <FormItem
              className={style.intervalWrapper}
              label={
                <FormLabelWithHelp
                  labelString='重复次数'
                  helpInfo='当一段代码重复次数达到指定区间才认为是有风险的'
                />
              }
            >
              <FormItem name='dup_min_dup_times' className={style.interval}>
                <InputNumber
                  readonly={readonly}
                  theme="normal"
                  placeholder='最小默认2'
                />
              </FormItem>
              <span className={style.splitLine} />
              <FormItem name='dup_max_dup_times' className={style.interval}>
                <InputNumber
                  readonly={readonly}
                  theme="normal"
                  placeholder='为空默认无限大'
                />
              </FormItem>
            </FormItem>
            <FormItem
              name='dup_issue_limit'
              label={
                <FormLabelWithHelp
                  labelString='上报限制'
                  helpInfo='限制上报的重复代码块数，可以减少开发的压力，提高修复积极性'
                />
              }
            >
              <InputNumber readonly={readonly} theme="normal" placeholder='默认1000' style={{ width: 130 }} />
            </FormItem>
          </>
        )
      }
      <FormLabelWithHelp
        size='large'
        labelString='代码统计'
        helpInfo='从目录和业务纬度统计代码行数，也可以获取提交记录便于代码Review。'
      />
      <FormItem label='是否启用' name='cloc_scan_enabled'>
        <Switch
          disabled={readonly}
          size='small'
          onChange={(checked: boolean) => update({
            cloc_scan_enabled: checked,
          }, `代码统计${checked ? '开启' : '关闭'}`)}
        />
      </FormItem>
      {
        !readonly && (
          <FormItem style={{ marginTop: 30 }}>
            <Button theme='primary' type='submit' style={{ marginRight: 10 }}>保存</Button>
            <Button theme='default' type='reset'>取消</Button>
          </FormItem>
        )
      }
    </Form>
  );
};

export default CodeMetricsForm;
