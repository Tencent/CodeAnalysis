/**
 * 创建工具弹框
 */

import React from 'react';
import { useHistory } from 'react-router-dom';
import { Modal, Form, Input, Checkbox, Select, message } from 'coding-oa-uikit';

import { getToolsRouter } from '@src/utils/getRoutePath';
import { createTool } from '@src/services/tools';
import { REPO_TYPE_OPTIONS, REPO_TYPE } from './constants';
import { SCM_MAP } from '@src/common/constants/authority';

import Authority from '@src/components/authority';

const { TextArea } = Input;
const { Option } = Select;

const layout = {
  labelCol: { span: 5 },
  wrapperCol: { span: 19 },
};

interface CreateToolModalProps {
  orgId: string;
  visible: boolean;
  onClose: () => void;
}

const CreateToolModal = (props: CreateToolModalProps) => {
  const [form] = Form.useForm();
  const history = useHistory();
  const { orgId, visible, onClose } = props;
  
  const onFinish = (data: any) => {
    const newFormData = data;
    if (newFormData.scm) {
      const [authType, id] = newFormData?.scm?.split('#') ?? [];
      delete data.scm;
      data.scm_auth = { auth_type: authType };
      if (SCM_MAP[authType]) {
        data.scm_auth[SCM_MAP[authType]] = id;
      }
    }

    createTool(orgId, newFormData).then((res) => {
      message.success('创建成功');
      history.push(`${getToolsRouter(orgId)}/${res.id}/tool-libs`);
    });
  };

  return (
    <Modal
      title='创建工具'
      width={600}
      visible={visible}
      // okButtonProps={{ loading }}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <Form {...layout} form={form} initialValues={{ scm_type: REPO_TYPE.GIT }}>
        <Form.Item
          label="工具名称"
          name="name"
          rules={[{
            required: true,
            message: '请输入工具名称!',
          }, {
            pattern: /^[A-Za-z0-9_-]+$/,
            message: '仅支持英文、数字、中划线或下划线',
          }]}
        >
          <Input placeholder="仅支持英文、数字、中划线或下划线" />
        </Form.Item>
        <Form.Item
          label="工具展示名称"
          name="display_name"
          rules={[{ required: true, message: '请输入前端展示名称' }]}
        >
          <Input placeholder="请使用大驼峰命名，如PyLint。" />
        </Form.Item>
        <Form.Item
          label="工具描述"
          name="description"
          rules={[{ required: true, message: '请输入工具描述' }]}
        >
          <TextArea placeholder="长度限制256个字符。" rows={3} />
        </Form.Item>
        <Form.Item
          label="工具仓库地址"
          name="scm_url"
          rules={[{ required: true, message: '请输入工具仓库地址' }]}
        >
          <Input.Group compact>
            <Form.Item name='scm_type' noStyle>
              <Select style={{ width: 70 }}>
                {REPO_TYPE_OPTIONS.map((item: string, index) => (
                  <Option key={index} value={item}>
                    {item.toUpperCase()}
                  </Option>
                ))}
              </Select>
            </Form.Item>
            <Form.Item
              name='scm_url'
              noStyle
            >
              <Input style={{ width: 357 }} />
            </Form.Item>
          </Input.Group>
        </Form.Item>
        <Authority
          form={form}
          name='scm'
          label='凭证'
          selectStyle={{ width: 360 }}
          placeholder='拉取代码库所需的凭证'
        />
        <Form.Item
          label="执行命令"
          name="run_cmd"
          rules={[{ required: true, message: '请输入执行命令' }]}
        >
          <Input placeholder="该命令的工作目录为工具库根目录。" />
        </Form.Item>
        <Form.Item label="环境变量" name="envs">
          <TextArea
            rows={3}
            placeholder="示例：PYTHON_HOME = $PYTHON#&_HOMEPATH = $PYTHON_HOME/bin:$PATH"
          />
        </Form.Item>
        <Form.Item label="License" name="license">
          <Input placeholder="许可证" />
        </Form.Item>
        <Form.Item label="" name="build_flag" valuePropName="checked">
          <Checkbox>是否为编译型工具</Checkbox>
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default CreateToolModal;
