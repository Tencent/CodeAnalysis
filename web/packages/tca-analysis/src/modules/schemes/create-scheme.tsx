// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      创建分析方案
 * author           luochunlan@coding.net
 * create at        2020-10-28
 */

import React, { useEffect } from 'react';
import { pick, find, trim } from 'lodash';
import { Form, Input, Checkbox, Radio, Select, message, Dialog, Tag } from 'tdesign-react';
import cn from 'classnames';

import { SCAN_LIST } from '@src/constant';
import { createScheme, copyScheme } from '@src/services/schemes';
import NodeTag from '@src/components/node-tag';

import style from './style.scss';

const { Option } = Select;
const { FormItem } = Form;

interface IProps {
  orgSid: string;
  teamName: string;
  visible: boolean;
  repoId: number | string;
  tags: any[]; // 运行环境列表
  languages: any[];
  schemeList: any[]; // 当前代码库分析方案列表
  templates: any[]; // 模板列表
  onClose: () => void;
  callback: (id: number) => void; // 创建完成之后的回调
}

const CreatSchemeModal = (props: IProps) => {
  const { orgSid, teamName, visible, tags, languages, schemeList, repoId, templates, onClose, callback } = props;
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.reset();
    }
  }, [visible, form]);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validate().then((result: any) => {
      if (result === true) {
        const data = form?.getFieldsValue(true);
        onFinish(data);
      }
    });
  };

  const onFinish = (data: any) => {
    if (find(schemeList, { name: trim(data.name) })) {
      message.error('存在同名的分析方案，请重新修改分析方案名称，保证方案名称唯一');
      return;
    }

    if (data.createType === 'create') {
      const { funcList = [] } = data;
      createScheme(orgSid, teamName, repoId, {
        ...pick(data, ['name', 'languages', 'tag']),
        ...SCAN_LIST.map(item => ({ [item.value]: funcList.includes(item.value) })).reduce(
          (acc, cur) => ({ ...acc, ...cur }),
          {},
        ),
        build_cmd: null,
        envs: null,
        pre_cmd: null,
        name: trim(data.name),
      }).then((res) => {
        message.success('创建成功');
        callback(res.scan_scheme);
        onClose();
      });
    } else {
      copyScheme(orgSid, teamName, repoId, {
        ...pick(data, ['name', 'ref_scheme']),
      }).then((res) => {
        message.success('创建成功');
        callback(res.scan_scheme);
        onClose();
      });
    }
  };

  return (
    <Dialog
      header="新建分析方案"
      className={style.schemeCreateModal}
      visible={visible}
      onClose={onClose}
      onConfirm={onSubmitHandle}
    >
      <Form layout="vertical" labelAlign='top' form={form} resetType='initial'>
        <FormItem
          name="createType"
          label="创建方式"
          initialData="create"
          rules={[{ required: true, message: '请选择创建方式' }]}
        >
          <Radio.Group>
            <Radio value="create">普通创建</Radio>
            <Radio value="template">模板创建</Radio>
            <Radio value="copy">复制已有分析方案</Radio>
          </Radio.Group>
        </FormItem>
        <Form.FormItem shouldUpdate={(prev, next) => prev.createType !== next.createType}>
          {({ getFieldValue }) => {
            switch (getFieldValue('createType')) {
              case 'copy':
                return (<>
                  <FormItem
                    name="ref_scheme"
                    rules={[
                      { required: true, message: '请选择分析方案ID' },
                    ]}
                  >
                    <Select
                      placeholder="请选择分析方案"
                      style={{ width: '100%' }}
                      options={schemeList}
                      keys={{
                        value: 'id',
                        label: 'name',
                      }}
                    />
                  </FormItem>
                  <FormItem
                    name="name"
                    label="方案名称"
                    rules={[
                      { required: true, message: '请输入方案名称' },
                      { max: 127, message: '方案名称过长' },
                    ]}
                  >
                    <Input placeholder="请输入方案名称" />
                  </FormItem>
                </>);
              case 'template':
                return (<>
                  <FormItem
                    name="ref_scheme"
                    rules={[{ required: true, message: '请选择模板' }]}
                  >
                    <Select
                      placeholder="请选择模板"
                      style={{ width: '100%' }}
                      onChange={(value: string, item: any) => form.setFieldsValue({ name: item.label })}
                    >
                      {templates.map(item => (
                        <Option key={item.id} value={item.id} label={item.name} className={style.optionWrapper}>
                          <div className={style.tmpl}>
                            <span>{item.name}</span>
                            <Tag className={cn(style.tmplTag, { [style.sys]: item.scheme_key === 'public' })}
                            >{item.scheme_key === 'public' ? '系统' : '自定义'}</Tag>
                          </div>
                        </Option>
                      ))}
                    </Select>
                  </FormItem>
                  <FormItem
                    name="name"
                    label="方案名称"
                    rules={[
                      { required: true, message: '请输入方案名称' },
                      { max: 127, message: '方案名称过长' },
                    ]}
                  >
                    <Input placeholder="请输入方案名称" />
                  </FormItem>
                </>);
              default:
                return (<>
                  <FormItem
                    name="name"
                    label="方案名称"
                    rules={[
                      { required: true, message: '请输入方案名称' },
                      { max: 127, message: '方案名称过长' },
                    ]}
                  >
                    <Input placeholder="请输入方案名称" />
                  </FormItem>
                  <FormItem
                    name="languages"
                    label="分析语言"
                    rules={[{ required: true, message: '请选择分析语言' }]}
                  >
                    <Select
                      placeholder="请选择分析语言"
                      style={{ width: '100%' }}
                      multiple
                      filterable
                      showArrow
                      options={languages}
                      keys={{
                        value: 'name',
                        label: 'display_name',
                      }}
                    />
                  </FormItem>
                  <NodeTag
                    name="tag"
                    label="运行环境"
                    rules={[{ required: true, message: '请选择运行环境' }]}
                    tags={tags}
                  />
                  <FormItem
                    name="funcList"
                    label="功能开启"
                    initialData={[
                      'lint_enabled',
                      'cc_scan_enabled',
                      'dup_scan_enabled',
                      'cloc_scan_enabled',
                    ]}
                    style={{ marginBottom: 0 }}
                  >
                    <Checkbox.Group options={SCAN_LIST} />
                  </FormItem>
                </>);
            }
          }}
        </Form.FormItem>
      </Form>
    </Dialog>
  );
};

export default CreatSchemeModal;
