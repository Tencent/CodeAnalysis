// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * description      创建方案模板
 */

import React from 'react';
import { useHistory } from 'react-router-dom';
import { pick, trim } from 'lodash';
import { Form, Input, Checkbox, Row, Col, Select, message, Modal } from 'coding-oa-uikit';

import { SCAN_LIST } from '../schemes/constants';
import { createTmpl } from '@src/services/template';
import NodeTag from '@src/components/node-tag';

import style from './style.scss';

const { Option } = Select;

interface IProps {
  orgSid: string;
  visible: boolean;
  tags: any[]; // 运行环境列表
  languages: any[];
  onClose: () => void;
}

const CreatSchemeModal = (props: IProps) => {
  const history = useHistory();
  const { orgSid, visible, tags, languages, onClose } = props;

  const [form] = Form.useForm();

  const onFinish = (data: any) => {
    const { funcList = [] } = data;
    createTmpl(orgSid, {
      ...pick(data, ['name', 'languages', 'tag', 'description']),
      ...SCAN_LIST.map(item => ({ [item.value]: funcList.includes(item.value) })).reduce(
        (acc, cur) => ({ ...acc, ...cur }),
        {},
      ),
      build_cmd: null,
      envs: null,
      pre_cmd: null,
      name: trim(data.name),
    }).then((res: any) => {
      message.success('创建成功');
      onReset();
      history.push(`${location.pathname}/${res.id}`);
    });
  };

  const onReset = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title="创建分析模板"
      width={520}
      className={style.schemeCreateModal}
      visible={visible}
      onCancel={onReset}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form layout="vertical" form={form} onFinish={onFinish}>
        <Form.Item
          name="name"
          label="模板名称"
          rules={[
            { required: true, message: '请输入模板名称' },
            { max: 127, message: '模板名称过长' },
          ]}
        >
          <Input placeholder="请输入模板名称" />
        </Form.Item>
        <Form.Item
          name="languages"
          label="分析语言"
          rules={[{ required: true, message: '请选择分析语言' }]}
        >
          <Select
            placeholder="请选择分析语言"
            style={{ width: '100%' }}
            mode='multiple'
            optionFilterProp='children'
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
          name="description"
          label="模板描述"
        >
          <Input.TextArea rows={3} placeholder="请输入模板描述" />
        </Form.Item>
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
      </Form>
    </Modal >
  );
};

export default CreatSchemeModal;
