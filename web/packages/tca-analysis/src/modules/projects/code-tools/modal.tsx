// Copyright (c) 2021-2024 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 启动任务
 */
import React, { useState } from 'react';
import moment from 'moment';
import cn from 'classnames';
import { mapValues, pickBy } from 'lodash';
import { Form, Input, Select, DatePicker, Modal } from 'coding-oa-uikit';

import { createToolScans } from '@src/services/projects';
import style from './style.scss';

const { Option } = Select;

interface IProps {
  visible: boolean;
  params: any;
  scanParams: any;
  onHide: () => void;
  callback: () => void;
}

const ScanModal = (props: IProps) => {
  const { visible, scanParams, params, onHide, callback } = props;
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const getComponent = (item: any) => {
    const { component, component_options: options, helper } = item;
    switch (component) {
      case 'date': {
        return (
          <DatePicker
            className={style.dataPicker}
            size="middle"
            style={{ width: '100%' }}
          />
        );
      }
      case 'input': {
        return <Input placeholder={helper && helper} />;
      }
      case 'select': {
        return (
          <Select>
            {options?.split(';').map((value: string) => (
              <Option key={value} value={value}>
                {value}
              </Option>
            ))}
          </Select>
        );
      }
      default: {
        return;
      }
    }
  };

  const onFinish = (formData: any) => {
    const { repoId, projectId, toolName } = params;
    const data = mapValues(formData, item => (item instanceof moment ? moment(item).format('YYYY-MM-DD') : item));

    setLoading(true);
    createToolScans(
      repoId,
      projectId,
      toolName,
      pickBy(data, value => value),
    )
      .then(() => {
        callback();
        onReset();
      })
      .finally(() => {
        setLoading(false);
      });
  };

  const onReset = () => {
    form.resetFields();
    onHide();
  };

  return (
    <Modal
      title="启动任务"
      width={480}
      className={style.scanModal}
      visible={visible}
      onCancel={onReset}
      okButtonProps={{
        loading,
      }}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form layout="vertical" form={form} onFinish={onFinish}>
        {scanParams.map((item: any, index: number) => (
          <Form.Item
            key={item.name}
            className={cn({
              [style.lastFormItem]: index === scanParams.length - 1,
            })}
            label={item.label}
            name={item.name}
            rules={[
              {
                required: item.component_required,
                message: `请输入${item.label}`,
              },
            ]}
          >
            {getComponent(item)}
          </Form.Item>
        ))}
      </Form>
    </Modal>
  );
};

export default ScanModal;
