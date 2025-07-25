// Copyright (c) 2021-2025 THL A29 Limited
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
import { Form, Input, Textarea, Checkbox, Row, Col, Select, message, Dialog } from 'tdesign-react';

import { SCAN_LIST } from '@src/constant';
import { createTmpl } from '@src/services/template';
import NodeTag from '@src/components/node-tag';

import style from './style.scss';

const { FormItem } = Form;

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

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validate().then((result: any) => {
      if (result === true) {
        const data = form.getFieldsValue(true);
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
      }
    });
  };

  const onReset = () => {
    form.reset();
    onClose();
  };

  return (
    <Dialog
      header="创建分析模板"
      className={style.schemeCreateModal}
      visible={visible}
      onClose={onReset}
      onConfirm={onSubmitHandle}
    >
      <Form
        layout="vertical"
        form={form}
        labelAlign='top'
        resetType='initial'
      >
        <FormItem
          name="name"
          label="模板名称"
          rules={[
            { required: true, message: '请输入模板名称' },
            { max: 127, message: '模板名称过长' },
          ]}
        >
          <Input placeholder="请输入模板名称" />
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
            showArrow
            filterable
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
          name="description"
          label="模板描述"
        >
          <Textarea rows={3} placeholder="请输入模板描述" />
        </FormItem>
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
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default CreatSchemeModal;
