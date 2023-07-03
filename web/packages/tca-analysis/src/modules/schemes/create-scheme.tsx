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

import React from 'react';
import { pick, find, trim } from 'lodash';
import { Form, Input, Checkbox, Radio, Row, Col, Select, message, Modal, Tag } from 'coding-oa-uikit';
import cn from 'classnames';

import { SCAN_LIST } from './constants';
import { createScheme, copyScheme } from '@src/services/schemes';
import NodeTag from '@src/components/node-tag';

import style from './style.scss';

const { Option } = Select;

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
    <Modal
      title="新建分析方案"
      width={520}
      className={style.schemeCreateModal}
      visible={visible}
      onCancel={onClose}
      afterClose={() => form.resetFields()}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form layout="vertical" form={form} onFinish={onFinish}>
        <Form.Item
          name="createType"
          label="创建方式"
          initialValue="create"
          rules={[{ required: true, message: '请选择创建方式' }]}
        >
          <Radio.Group
            onChange={(e: any) => {
              form.resetFields();
              form.setFieldsValue({ createType: e.target.value });
            }}
          >
            <Row gutter={12}>
              <Col span={7}>
                <Radio value="create">普通创建</Radio>
              </Col>
              <Col span={7}>
                <Radio value="template">模板创建</Radio>
              </Col>
              <Col span={10}>
                <Radio value="copy">复制已有分析方案</Radio>
              </Col>
            </Row>
          </Radio.Group>
        </Form.Item>
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.createType !== currentValues.createType
          }
        >
          {({ getFieldValue }) => {
            switch (getFieldValue('createType')) {
              case 'copy':
                return (
                  <>
                    <Form.Item
                      name="ref_scheme"
                      rules={[
                        { required: true, message: '请选择分析方案ID' },
                      ]}
                    >
                      <Select
                        placeholder="请选择分析方案"
                        style={{ width: '100%' }}
                      >
                        {schemeList.map(item => (
                          <Option key={item.id} value={item.id}>
                            {item.name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <Form.Item
                      name="name"
                      label="方案名称"
                      rules={[
                        { required: true, message: '请输入方案名称' },
                        { max: 127, message: '方案名称过长' },
                      ]}
                    >
                      <Input placeholder="请输入方案名称" />
                    </Form.Item>
                  </>
                );

              case 'template':
                return (
                  <>
                    <Form.Item
                      name="ref_scheme"
                      rules={[{ required: true, message: '请选择模板' }]}
                    >
                      <Select
                        placeholder="请选择模板"
                        style={{ width: '100%' }}
                        optionLabelProp="label"
                        onChange={(value: string, item: any) => form.setFieldsValue({ name: item.label })
                        }
                      >
                        {templates.map(item => (
                          <Option key={item.id} value={item.id} label={item.name}>
                            <div className={style.tmpl}>
                              <span>{item.name}</span>
                              <Tag className={cn(style.tmplTag, { [style.sys]: item.scheme_key === 'public' })}
                              >{item.scheme_key === 'public' ? '系统' : '自定义'}</Tag>
                            </div>
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <Form.Item
                      name="name"
                      label="方案名称"
                      rules={[
                        { required: true, message: '请输入方案名称' },
                        { max: 127, message: '方案名称过长' },
                      ]}
                    >
                      <Input placeholder="请输入方案名称" />
                    </Form.Item>
                  </>
                );
              default:
                return (
                  <>
                    <Form.Item
                      name="name"
                      label="方案名称"
                      rules={[
                        { required: true, message: '请输入方案名称' },
                        { max: 127, message: '方案名称过长' },
                      ]}
                    >
                      <Input placeholder="请输入方案名称" />
                    </Form.Item>

                    <Form.Item
                      name="languages"
                      label="分析语言"
                      rules={[{ required: true, message: '请选择分析语言' }]}
                    >
                      <Select
                        placeholder="请选择分析语言"
                        style={{ width: '100%' }}
                        mode="multiple"
                        optionFilterProp="children"
                        showArrow
                      >
                        {languages.map(item => (
                          <Option key={item.name} value={item.name}>
                            {item.display_name}
                          </Option>
                        ))}
                      </Select>
                    </Form.Item>
                    <NodeTag
                      name="tag"
                      label="运行环境"
                      rules={[{ required: true, message: '请选择运行环境' }]}
                      tags={tags}
                    />
                    <Form.Item
                      name="funcList"
                      label="功能开启"
                      initialValue={[
                        'lint_enabled',
                        'cc_scan_enabled',
                        'dup_scan_enabled',
                        'cloc_scan_enabled',
                      ]}
                      style={{ marginBottom: 0 }}
                    >
                      <Checkbox.Group>
                        <Row gutter={16}>
                          {SCAN_LIST.map((item: any) => (
                            <Col span={6} key={item.value}>
                              <Checkbox value={item.value}>
                                {item.label}
                              </Checkbox>
                            </Col>
                          ))}
                        </Row>
                      </Checkbox.Group>
                    </Form.Item>
                  </>
                );
            }
          }}
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreatSchemeModal;
