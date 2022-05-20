/**
 * 新增/编辑弹框
 */
import React, { useState, useEffect } from 'react';
import cn from 'classnames';
import { isEmpty, compact } from 'lodash';
import { Modal, Form, Select, Input, Tag, Tooltip, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';

import { LIB_ENV, LibTypeEnum, LIB_TYPE } from '@src/modules/tool-libs/constants';
import { getToolLibs, addToolSchemes, updateToolSchemes } from '@src/services/tools';

import style from './style.scss';

const { Option } = Select;
const { TextArea } = Input;
const layout = {
  labelCol: { span: 4 },
  wrapperCol: { span: 20 },
};
const defaultFields = [{
  name: 0,  // 字段顺序
  key: 0  // react key，不随顺序更改
}];

interface UpdateLibSchemeModalProps {
  orgSid: string;
  toolId: number;
  visible: boolean;
  initData: any;
  onClose: () => void;
  callback: () => void;
}

const UpdateLibSchemeModal = (props: UpdateLibSchemeModalProps) => {
  const { orgSid, toolId, visible, initData, onClose, callback } = props;
  const [form] = Form.useForm();
  const [toolLibs, setToolLibs] = useState<Array<any>>([]);
  const [fields, setFields] = useState<Array<any>>(defaultFields);
  const [maxFieldKey, setMaxFieldKey] = useState<number>(0);  // tool_libs max key

  const isEdit = initData && !isEmpty(initData);

  useEffect(() => {

    if (visible) {
      if (isEdit) {  // 编辑
        initFields();
        form.setFieldsValue({
          ...initData,
          scheme_os: initData?.scheme_os?.split(';'),
          tool_libs: initData?.toollib_maps?.map((item: any) => item.toollib.id) ?? []
        })
      } else {  // 新增
        form.resetFields();
      }
    }

  }, [visible])

  useEffect(() => {
    getToolLibs(orgSid, {
      offset: 0,
      limit: 100
    }).then((res) => {
      setToolLibs(res.results);
    })
  }, [orgSid])

  /**
  * 设置工具依赖表单初始值
  * @param schemeId 依赖方案 ID
  */
  const initFields = () => {
    const arrs = initData?.toollib_maps?.map((item: any, index: number) => ({
      name: index,
      key: index
    })) ?? defaultFields;

    if (!isEmpty(arrs)) {
      setFields(arrs);
      setMaxFieldKey(arrs.length - 1);
    }
  }

  const add = (index: number) => {
    const arrs = fields;

    if (index >= 0 && index <= arrs.length) {
      const values = form.getFieldValue('tool_libs') || [];
      form.setFieldsValue({
        tool_libs: [
          ...values.slice(0, index + 1),
          undefined,
          ...values.slice(index + 1)
        ]
      })
      setFields([
        ...arrs.slice(0, index + 1),
        {
          name: index + 1,
          key: maxFieldKey + 1
        },
        ...arrs.slice(index + 1).map((item) => ({
          ...item,
          name: item.name + 1
        }))
      ]);

      setMaxFieldKey(maxFieldKey + 1)
    }
  }

  const remove = (index: number) => {
    const values = form.getFieldValue('tool_libs');
    const arrs = fields;

    values.splice(index, 1);
    form.setFieldsValue({ tool_libs: values });

    setFields([
      ...arrs.slice(0, index),
      ...arrs.slice(index + 1).map((item) => ({
        ...item,
        name: item.name - 1
      }))
    ])
  }

  const onFinish = (formData: any) => {
    const params = {
      ...formData,
      condition: formData.condition || null,
      scheme_os: formData.scheme_os?.join(';'),
      tool_libs: compact(formData.tool_libs)?.map((id: number) => ({ toollib: id })),
    };
    if (isEdit) {
      updateToolSchemes(orgSid, toolId, initData.id, params).then(() => {
        callback();
        message.success('依赖方案编辑成功');
        onClose();
      })
    } else {
      addToolSchemes(orgSid, toolId, params).then(() => {
        message.success('依赖方案添加成功');
        callback();
        onClose();
      })
    }
  }

  return (
    <Modal
      title={`${isEdit ? '编辑' : '添加'}依赖配置`}
      width={604}
      visible={visible}
      className={style.updateSchemeModal}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={() => form.validateFields().then(onFinish)}
    >
      <Form {...layout} form={form}>
        <Form.Item
          label="适用系统"
          name="scheme_os"
        >
          <Select mode='multiple'>
            {
              Object.entries(LIB_ENV).map(([key, text]) => (
                <Option key={key} value={key}>{text}</Option>
              ))
            }
          </Select>
        </Form.Item>
        <Form.Item
          label="判断条件"
          name="condition"
        >
          <TextArea rows={3} placeholder='仅支持=条件' />
        </Form.Item>
        <Form.Item label='工具依赖' {...layout} required>
          {
            fields.map((item, index) => {
              return (
                <Form.Item key={item.key}>
                  <Form.Item
                    {...item}
                    rules={[{
                      required: true,
                      message: '请选择工具依赖',
                    }]}
                    name={['tool_libs', item.name]}
                    noStyle
                  >
                    <Select
                      showSearch
                      optionFilterProp="label"
                      style={{ width: '400px' }}
                      optionLabelProp="label"
                      onChange={(value: string, item: any) => form.setFieldsValue({ name: item.label })}
                    >
                      {toolLibs.map(item => (
                        <Option key={item.id} value={item.id} label={item.name}>
                          <div className={style.lib}>
                            <span>{item.name}</span>
                            <Tag className={cn(style.libTag, { [style.privite]: item.lib_type === LibTypeEnum.PRIVATE })}
                            >{LIB_TYPE[item.lib_type]}</Tag>
                          </div>
                        </Option>
                      ))}
                    </Select>
                  </Form.Item>
                  <Tooltip title='添加' getPopupContainer={() => document.body}>
                    <PlusIcon
                      className={style.addIcon}
                      onClick={() => {
                        add(index);
                      }}
                    />
                  </Tooltip>
                  {
                    fields.length > 1 && (
                      <Tooltip title='删除' getPopupContainer={() => document.body}>
                        <TrashIcon
                          className={style.delIcon}
                          onClick={() => {
                            remove(index);
                          }}
                        />
                      </Tooltip>

                    )
                  }
                </Form.Item>
              )
            })
          }
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default UpdateLibSchemeModal;