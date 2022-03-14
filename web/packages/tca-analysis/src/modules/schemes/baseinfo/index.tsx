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
  Input,
  Radio,
  Row,
  Col,
  Select,
  Button,
  Dropdown,
  Menu,
  message,
  Modal,
} from 'coding-oa-uikit';
import EllipsisH from 'coding-oa-uikit/lib/icon/EllipsisH';

import { updateSchemeBasic, getLintConfig, updateLintConfig } from '@src/services/schemes';

import style from './style.scss';
import formStyle from '../style.scss';

const { Option } = Select;
const layout = {
  labelCol: { span: 6 },
  wrapperCol: { span: 18 },
  colon: false,
};

interface BaseConfigProps {
  orgSid: string;
  teamName: string;
  repoId: string | number;
  tags: any[];
  languages: any[];
  data: any;
  callback?: (data: any) => void;
}

const BaseConfig = (props: BaseConfigProps) => {
  const { orgSid, teamName, data, repoId, tags, languages, callback } = props;
  const [form] = Form.useForm();
  const [visible, setVisible] = useState(false);
  const [isDefault, setDefault] = useState(true);
  const [lintConfig, setLintConfig] = useState<any>({});
  const schemeId = data.id;

  useEffect(() => {
    if (schemeId) {
      getLintConfig(orgSid, teamName, repoId, data.id).then(res => setLintConfig(res));
    }
  }, [schemeId]);

  useEffect(() => form.resetFields(), [schemeId, lintConfig.envs]);

  // todo: remove
  const openModal = ({ key }: { key: string }) => {
    if (key === 'restore') {
      onFinish({ ...data, status: 1 });
    } else {
      setVisible(true);
      setDefault(key === 'default');
    }
  };

  const onFinish = (formData: any) => {
    updateSchemeBasic(orgSid, teamName, repoId, schemeId, { ...data, ...formData }).then((response: any) => {
      message.success('更新成功');
      callback?.(response);
    });

    if (formData.envs !== lintConfig.envs) {
      updateLintConfig(orgSid, teamName, repoId, schemeId, {
        ...lintConfig,
        envs: formData.envs,
      }).then((res) => {
        setLintConfig(res);
      });
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

  return (
    <>
      <Form
        labelAlign="left"
        className={cn(style.baseConfig, formStyle.schemeFormVertical)}
        initialValues={{ ...data, envs: lintConfig.envs }}
        form={form}
        onFinish={onFinish}
      >
        <Form.Item
          {...layout}
          name="name"
          label="方案名称"
          rules={[
            { required: true, message: '请输入方案名称' },
            { max: 127, message: '方案名称过长' },
          ]}
        >
          <Input placeholder="请输入方案名称" />
        </Form.Item>
        <Form.Item {...layout} name="description" label="方案描述">
          <Input.TextArea rows={3} placeholder="请输入方案描述" />
        </Form.Item>
        <Form.Item
          {...layout}
          name="languages"
          label="分析语言"
          rules={[{ required: true, message: '请选择分析语言' }]}
        >
          <Select
            mode="multiple"
            placeholder="请选择分析语言"
            optionFilterProp="children"
          >
            {languages.map(item => (
              <Option key={item.name} value={item.name}>
                {item.display_name}
              </Option>
            ))}
          </Select>
        </Form.Item>
        <Form.Item
          {...layout}
          name="tag"
          label="运行环境"
          rules={[{ required: true, message: '请选择运行环境' }]}
        >
          <Radio.Group>
            <Row>
              {tags.map(item => item.public && (
                <Col title={item.name} span={8} key={item.name}>
                  <Radio value={item.name} className={style.radio}>
                    {item.name}
                  </Radio>
                </Col>
              ))}
            </Row>
          </Radio.Group>
        </Form.Item>
        <Form.Item {...layout} name="envs" label="环境变量">
          <Input.TextArea rows={3} placeholder="请输入环境变量" />
        </Form.Item>
        <Form.Item style={{ marginTop: 30 }}>
          <Button type="primary" htmlType="submit" style={{ marginRight: 10 }}>
            保存
          </Button>
          <Button onClick={() => form.resetFields()}>取消</Button>
          <Dropdown
            overlay={
              <Menu onClick={openModal}>
                {data.status === 2 && <Menu.Item key="restore">恢复方案</Menu.Item>}
                {data.status === 1 && !data.default_flag && (
                  <Menu.Item key="default">设为默认方案</Menu.Item>
                )}
                {data.status === 1 && (
                  <Menu.Item
                    key="deprecated"
                    style={{ color: data.default_flag ? '#c5cedb' : '#eb333f' }}
                    disabled={data.default_flag}
                  >
                    废弃方案
                  </Menu.Item>
                )}
              </Menu>
            }
          >
            <span className={formStyle.ellipsis}>
              <EllipsisH />
            </span>
          </Dropdown>
        </Form.Item>
      </Form>

      <Modal
        visible={visible}
        className={style.baseModal}
        onCancel={() => setVisible(false)}
        okButtonProps={{
          danger: !isDefault,
        }}
        onOk={setSchemeStatus}
      >
        <h2 className={style.title}>{isDefault ? '设为默认方案' : '废弃方案'}</h2>
        <p>
          {isDefault
            ? '建议默认分析方案用于主干代码分析，请谨慎操作！'
            : '废弃该方案将导致关联的分支项目关闭，确定要废弃该方案？请查看关联分支列表，慎重操作！'}
        </p>
      </Modal>
    </>
  );
};

export default BaseConfig;
