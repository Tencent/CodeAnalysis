/**
 * 启动分析模态框
 */

import React, { useState } from 'react';
import { saveAs } from 'file-saver';

import { Modal, Radio, Form, Input, message } from 'coding-oa-uikit';

import { downloadIniFile } from '@src/services/projects';

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

  const [type, setType] = useState(true);
  const [loading, setLoading] = useState(false);
  const { orgSid, teamName, visible, projectId, repoId, onClose } = props;

  const onReset = () => {
    setType(true);
    onClose();
  };

  const onFinish = (data: any) => {
    setLoading(true);
    downloadIniFile(orgSid, teamName, repoId, projectId, {
      ...data,
      total_scan: data.total_scan === 2,
    })
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
  };


  return (
    <Modal
      title="启动分析"
      width={466}
      className={style.antModalScanModal}
      visible={visible}
      onCancel={onReset}
      okText="下载配置文件"
      confirmLoading={loading}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <p className={style.desc}>
        推荐使用增量分析，仅对上次分析后提交的 diff 代码进行分析，速度更快！
      </p>
      <p className={style.desc}>全量分析将分析分支中全部文件，适合分析方案配置变更后执行。</p>
      <Form
        layout='vertical'
        form={form}
      >
        <Form.Item
          name="total_scan"
          label=""
          initialValue={1}
        >
          <Radio.Group onChange={e => setType(e.target.value)} value={type}>
            <Radio value={1}>增量分析</Radio>
            <Radio value={2}>全量分析</Radio>
          </Radio.Group>
        </Form.Item>
        <Form.Item
          name='source_dir'
          label='本地代码目录绝对路径'
          rules={[{ required: true, message: '请输入本地代码目录绝对路径' }]}
        >
          <Input placeholder='请输入本地代码目录绝对路径' />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default ScanModal;
