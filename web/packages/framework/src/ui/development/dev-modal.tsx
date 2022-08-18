import React, { useEffect, useState } from 'react';
import { unionBy } from 'lodash';
import { Modal, Button, Form, Input, Space } from 'coding-oa-uikit';
import Plus from 'coding-oa-uikit/lib/icon/Plus';
import Trash from 'coding-oa-uikit/lib/icon/Trash';
import { getLocalStorage, setLocalStorage, debug } from '@src/utils';
import Constant from '@src/constant';

interface DevModalProps {
  visible: boolean;
  onOk: (data: string) => void;
  onCancel: () => void;
}

const DevModal = ({ visible, onOk, onCancel }: DevModalProps) => {
  const [form] = Form.useForm();
  const [microApiList, setMicroApiList] = useState<Array<MicroDevApiList>>([]);
  useEffect(() => {
    if (visible) {
      try {
        setMicroApiList(JSON.parse(getLocalStorage(Constant.MICRO_FRONTEND_API_LIST)));
      } catch (e) {
        debug(e);
      }
      form.resetFields();
    }
  }, [visible]);

  const onSubmitHandle = () => {
    form.validateFields().then(({ microApiList }: { microApiList: Array<MicroDevApiList> }) => {
      const data = JSON.stringify(unionBy(microApiList.filter(microApi => microApi.name && microApi.url), 'name'));
      setLocalStorage(Constant.MICRO_FRONTEND_API_LIST, data);
      onOk(data);
    });
  };

  return <Modal
    visible={visible} width={600}
    title="Micro Frontend Dev"
    onOk={onSubmitHandle}
    onCancel={onCancel}
    okText="启用"
    cancelText="取消"
    afterClose={form.resetFields}
  >
    <Form name="dev-modal-form" layout="vertical" form={form}
      initialValues={{ microApiList }}>
      <Form.List name="microApiList">
        {(fields, { add, remove }) => (
          <Form.Item style={{ marginBottom: 0 }}
            label={

              <Button className="mb-sm"
                type="link"
                icon={<Plus />}
                onClick={() => {
                  add();
                }}
              >添加微前端开发环境地址</Button>
            }
          >
            {fields.map(field => (
              <Form.Item key={field.key}>
                <Space
                  key={field.key}
                  align="baseline"
                >
                  <Form.Item
                    {...field}
                    name={[field.name, 'name']}
                    noStyle
                  >
                    <Input placeholder="微前端" />
                  </Form.Item>
                  <Form.Item
                    {...field}
                    name={[field.name, 'url']}
                    noStyle
                  >
                    <Input placeholder="dev地址" style={{ width: '330px' }} />
                  </Form.Item>
                  <Trash
                    className="cursor-pointer"
                    onClick={() => {
                      remove(field.name);
                    }}
                  />
                </Space>
              </Form.Item>
            ))}
          </Form.Item>
        )}
      </Form.List>
    </Form>
  </Modal>;
};

export default DevModal;


