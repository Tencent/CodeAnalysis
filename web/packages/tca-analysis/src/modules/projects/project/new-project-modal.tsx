// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 新建分析项目模态框
 */

import React, { useState, useEffect } from 'react';
import { useHistory, Link } from 'react-router-dom';
import { get } from 'lodash';
import cn from 'classnames';
import { Modal, Input, Form, Select, Radio, Tag, Alert } from 'coding-oa-uikit';

import { getProjectRouter, getSchemeRouter } from '@src/utils/getRoutePath';
import { getProjects, createProject } from '@src/services/projects';
import { getNodes } from '@src/services/schemes';

import style from '../style.scss';

const { Option } = Select;

interface NewProjectModalProps {
  orgSid: string;
  teamName: string;
  visible: boolean;
  schemes: any;
  templates: any;
  repoId: number;
  onClose: () => void;
  callback?: (branch: string) => void;
}

const NewProjectModal = (props: NewProjectModalProps) => {
  const [form] = Form.useForm();
  const history = useHistory();
  const [loading, setLoading] = useState(false);
  const [noNode, setNoNode] = useState(false);
  const {
    orgSid,
    teamName,
    visible,
    repoId,
    schemes,
    templates,
    onClose,
    callback,
  } = props;

  useEffect(() => {
    getNodes(orgSid).then((res: any) => {
      if (!res?.count) {
        setNoNode(true);
      }
    });
  }, [visible]);

  const onFinish = async (data: any) => {
    setLoading(true);
    try {
      const res = await getProjects(orgSid, teamName, repoId, {
        branch: data.branch,
        scan_scheme: data.scan_scheme_id,
        limit: 1,
      });
      let project = get(res, 'results[0]', {});

      if (project.id && data.type !== 'template') {
        Modal.confirm({
          title: '分析项目已存在',
          content: '是否跳转到该分析项目？',
          onOk() {
            history.push(`${getProjectRouter(
              orgSid,
              teamName,
              repoId,
              project.id,
            )}/overview`);
            onReset();
          },
        });
      } else {
        if (data.type === 'template') {
          data.is_template = true;
        }
        delete data.type;

        project = await createProject(orgSid, teamName, repoId, data);

        if (project.id) {
          Modal.confirm({
            title: '分析项目已创建',
            content: '是否跳转到该分析项目？',
            onOk() {
              history.push(`${getProjectRouter(
                orgSid,
                teamName,
                repoId,
                project.id,
              )}/overview`);
              onReset();
              callback?.(project.branch);
            },
          });
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const onReset = () => {
    form.resetFields();
    onClose();
  };

  return (
    <Modal
      title="添加分析项目"
      className={style.newProjectModal}
      visible={visible}
      onCancel={onReset}
      okText="新建分析项目"
      confirmLoading={loading}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      {noNode && <Alert
        message={<p>团队未接入任何专机节点，可能导致分析失败。
          <br/>
          <a href={`/t/${orgSid}/nodes/`} target='_blank' rel="noreferrer">立即接入{'>>'}</a>
        </p>}
        type="warning"
        showIcon
        className={style.alert}
      />}
      <Form
        layout="vertical"
        form={form}
        onFinish={(data) => {
          onFinish(data);
        }}
        initialValues={{ type: 'scheme' }}
      >
        <Form.Item
          name="branch"
          label="分支名称"
          rules={[{ required: true, message: '请输入分支名称' }]}
        >
          <Input placeholder="请输入分支名称" />
        </Form.Item>
        <Form.Item
          name="scan_path"
          label="代码目录"
        >
          <Input placeholder='相对路径，默认为/' />
        </Form.Item>
        <Form.Item name="type" label="">
          <Radio.Group>
            <Radio value="scheme">分析方案</Radio>
            <Radio value="template">分析方案模板</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item
          noStyle
          shouldUpdate={(prevValues, currentValues) => prevValues.type !== currentValues.type
          }
        >
          {({ getFieldValue }) => (getFieldValue('type') === 'template' ? (
            <>
              <Form.Item
                name="global_scheme_id"
                label="分析方案模板"
                rules={[{ required: true, message: '请选择方案模板' }]}
              >
                <Select
                  showSearch
                  placeholder="请选择分析方案模板"
                  optionLabelProp="label"
                  optionFilterProp="label"
                  onChange={(id: number, option: any) => {
                    form.setFieldsValue({ custom_scheme_name: option.label });
                  }}
                >
                  {templates.map((item: any) => (
                    <Option key={item.id} value={item.id} label={item.name}>
                      <div className={style.tmpl}>
                        <span>{item.name}</span>
                        <Tag
                          className={cn(style.tmplTag, {
                            [style.sys]: item.scheme_key === 'public',
                          })}
                        >
                          {item.scheme_key === 'public' ? '系统' : '自定义'}
                        </Tag>
                      </div>
                    </Option>
                  ))}
                </Select>
              </Form.Item>
              <Form.Item
                name="custom_scheme_name"
                label="分析方案名称"
                style={{ marginBottom: 0 }}
                rules={[{ required: true, message: '请输入分析方案名称' }]}
              >
                <Input placeholder='请为所创建的分析方案命名' />
              </Form.Item>
              <p className={style.desc}>Tips: 根据模板创建项目实质是按照模板新增一份分析方案后创建项目</p>
              </>
          ) : (
              <Form.Item
                name="scan_scheme_id"
                label="分析方案"
                style={{ marginBottom: 0 }}
                rules={[{ required: true, message: '请选择分析方案' }]}
              >
                <Select
                  placeholder="请选择分析方案"
                  notFoundContent={
                    <p style={{ color: '#606c80' }}>
                      暂无分析方案，请
                      <Link to={`${getSchemeRouter(orgSid, teamName, repoId)}`}>
                        新建分析方案
                      </Link>
                    </p>
                  }
                >
                  {schemes.map((item: any) => (
                    <Option key={item.id} value={item.id}>
                      {item.name}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
          ))
          }
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default NewProjectModal;
