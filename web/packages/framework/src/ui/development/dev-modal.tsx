import React, { useEffect } from 'react';
import { unionBy } from 'lodash';
import { Form, Dialog, Button, Input, Switch } from 'tdesign-react';
import { AddIcon, MinusCircleIcon } from 'tdesign-icons-react';

import { getLocalStorage, setLocalStorage, debug } from '@src/utils';
import Constant from '@src/constant';

const { FormItem, FormList } = Form;

interface DevModalProps {
  visible: boolean;
  onOk: (data: string) => void;
  onCancel: () => void;
}

const DevModal = ({ visible, onOk, onCancel }: DevModalProps) => {
  const [form] = Form.useForm();
  useEffect(() => {
    if (visible) {
      try {
        const microApiList: MicroDevApiList[] = JSON.parse(getLocalStorage(Constant.MICRO_FRONTEND_API_LIST));
        form.setFieldsValue({ microApiList: microApiList.map(i => ({ url: i.url, enabled: i.enabled !== false })) });
      } catch (e) {
        debug(e);
      }
    }
  }, [visible, form]);

  const onConfirm = () => {
    form.validate().then((result) => {
      if (result === true) {
        const { microApiList } = form.getFieldsValue(true);
        const data = JSON.stringify(unionBy((microApiList as MicroDevApiList[]).filter(i => i.url).map((api) => {
          const { url } = api;
          const name = url.substring(url.lastIndexOf('/') + 1, url.lastIndexOf('.'));
          return { ...api, name };
        }), 'name'));
        setLocalStorage(Constant.MICRO_FRONTEND_API_LIST, data);
        onOk(data);
      }
    });
  };

  return <Dialog
    visible={visible}
    header="Micro Frontend Dev"
    onConfirm={onConfirm}
    onClose={onCancel}
    onCancel={onCancel}
    onClosed={form.reset}
  >
    <Form layout="vertical" form={form} >
      <FormList name={['microApiList']}>
        {(fields, { add, remove }) => (
          <>
            {fields.map(({ key, name, ...restField }) => (
              <FormItem key={key}  >
                <FormItem {...restField} name={[name, 'url']} style={{ width: '100%' }}>
                  <Input />
                </FormItem>
                <FormItem {...restField} name={[name, 'enabled']} initialData={true}>
                  <Switch />
                </FormItem>
                <FormItem>
                  <MinusCircleIcon size="20px" style={{ cursor: 'pointer' }} onClick={() => remove(name)} />
                </FormItem>
              </FormItem>
            ))}
            <FormItem>
              <Button icon={<AddIcon />} theme="default" variant="dashed" onClick={() => add({ province: 'bj', area: 'tzmax' })}>
                添加微前端开发环境地址
              </Button>
            </FormItem>
          </>
        )}
      </FormList>
    </Form>
  </Dialog>;
};

export default DevModal;


