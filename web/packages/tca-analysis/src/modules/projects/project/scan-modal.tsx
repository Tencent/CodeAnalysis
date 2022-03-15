// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 启动分析模态框
 */

import React, { useState } from 'react';
import { saveAs } from 'file-saver';
import { useHistory } from 'react-router-dom';
import { Modal, Radio, Form, Input, message } from 'coding-oa-uikit';

import { getProjectRouter } from '@src/utils/getRoutePath';
import { downloadIniFile, createJob } from '@src/services/projects';

import style from './style.scss';

interface ScanModalProps {
  orgSid: string;
  teamName: string;
  visible: boolean;
  projectId: number;
  repoId: number;
  onClose: () => void;
  callback?: () => void;
}

const ScanModal = (props: ScanModalProps) => {
  const [form] = Form.useForm();
  const history = useHistory();

  const [type, setType] = useState(true);
  const [loading, setLoading] = useState(false);
  const [scan, setScan] = useState('web');

  const { orgSid, teamName, visible, projectId, repoId, onClose } = props;

  const onReset = () => {
    onClose();
    form.resetFields();
  };

  const onFinish = (data: any) => {
    if (scan === 'client') {  // 客户端分析 - 下载配置文件
      setLoading(true);
      downloadIniFile(orgSid, teamName, repoId, projectId, data)
        .then((response: any) => response.text())
        .then((res: any) => {
          const blob = new Blob([res], { type: 'text/plain;charset=utf-8' });
          saveAs(blob, 'codedog.ini');
          message.success('下载成功');

          Modal.success({
            title: '下载配置文件成功',
            content: '请到客户端替换对应的 codedog.ini 文件',
          });
        })
        .finally(() => {
          setLoading(false);
        });
    } else {
      setLoading(true);
      createJob(orgSid, teamName, repoId, projectId, {
        incr_scan: data.total_scan,
      }).then(() => {
        onReset();
        history.push(
          `${getProjectRouter(orgSid, teamName, repoId, projectId)}/scan-history`,
          { refresh: Math.random() },
        );
      })
        .finally(() => {
          setLoading(false);
        });
    }
  };


  return (
    <Modal
      title="启动分析"
      width={466}
      className={style.antModalScanModal}
      visible={visible}
      onCancel={onReset}
      confirmLoading={loading}
      okText={scan === 'client' ? '下载配置文件' : '启动分析'}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <Form
        layout='vertical'
        form={form}
        initialValues={{
          scan: 'web',
          total_scan: true
        }}
      >
        <Form.Item
          name='scan'
          label=''
        >
          <Radio.Group
            value={scan}
            onChange={(e: any) => setScan(e.target.value)}
          >
            <Radio.Button value='web'>在线分析</Radio.Button>
            <Radio.Button value='client'>客户端分析</Radio.Button>
          </Radio.Group>
        </Form.Item>
        <Form.Item
          name="total_scan"
          label=""
        >
          <Radio.Group onChange={e => setType(e.target.value)} value={type}>
            <Radio value={true}>增量分析</Radio>
            <Radio value={false}>全量分析</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item noStyle shouldUpdate={(prevValues: any, curValues: any) => prevValues.scan !== curValues.scan}>
          {
            ({ getFieldValue }: { getFieldValue: any }) => getFieldValue('scan') === 'client' && (
              <Form.Item
                name='source_dir'
                label='本地代码目录绝对路径'
                rules={[{ required: true, message: '请输入本地代码目录绝对路径' }]}
              >
                <Input placeholder='请输入本地代码绝对路径' />
              </Form.Item>
            )
          }
        </Form.Item>
      </Form>
      <p className={style.desc}>
        推荐使用增量分析，仅对上次分析后提交的 diff 代码进行分析，速度更快！
      </p>
      <p className={style.desc}>全量分析将分析分支中全部文件，适合分析方案配置变更后执行。</p>
    </Modal>
  );
};

export default ScanModal;
