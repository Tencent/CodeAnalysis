/**
 * 依赖方案
 */
import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import { isEmpty, find, dropRight, compact } from 'lodash';

import { Form, Select, Input, Checkbox, Tooltip, Button, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';

import { getToolLibs, getToolSchemes, addToolSchemes, updateToolSchemes, delToolScheme } from '@src/services/tools';
import { LIB_ENV } from '@src/modules/tool-libs/constants';

import style from '../detail.scss';

const { Option } = Select;
const { TextArea } = Input;

interface LibSchemeProps {
  layout: any;
  orgSid: string;
  toolId: number;
  isEdit: boolean;
  getComponent: (editComponent: any, defaultData: any) => React.ReactDOM
}

const defaultFields = [{
  name: 0,  // 字段顺序
  key: 0  // react key，不随顺序更改
}];

const LibScheme = (props: LibSchemeProps) => {
  const [form] = Form.useForm();
  const { layout, orgSid, toolId, isEdit, getComponent } = props;
  const [toolSchemes, setToolSchemes] = useState([]);
  const [toolLibs, setToolLibs] = useState<Array<any>>([]);
  const [activeKey, setActiveKey] = useState(toolSchemes?.[0]?.id ?? -1); // 有依赖方案默认展示第一个，没有默认为新增依赖
  const [tabs, setTabs] = useState([]);
  // tool_libs max key
  const [maxFieldKey, setMaxFieldKey] = useState<number>(0);
  const [fields, setFields] = useState<Array<any>>(defaultFields);

  useEffect(() => {
    getToolLibs(orgSid, {
      offset: 0,
      limit: 10
    }).then((res) => {
      setToolLibs(res.results);
    })
  }, [orgSid])

  useEffect(() => getLibSchemes(), [toolId])

  useEffect(() => {
    if (activeKey) {
      initFields(activeKey);
      initFormFields(activeKey);
    }
  }, [activeKey])

  const getLibSchemes = (activeKey?: number) => {
    getToolSchemes(orgSid, toolId).then((res) => {
      setToolSchemes(res);
      initTabs(res, activeKey);
    })
  }

  const initTabs = (toolSchemes: any, activeKey?: number) => {
    const ids = toolSchemes.map((item: any) => item.id) ?? [];
    setTabs(ids);
    setActiveKey(activeKey || ids[0] || -1);
  }

  const initFormFields = (activeKey: number) => {
    const curScheme = find(toolSchemes, { id: activeKey }) ?? {};
    if (isEmpty(curScheme)) {  // 新增
      form.resetFields();
    } else {
      form.setFieldsValue({
        ...curScheme,
        scheme_os: curScheme?.scheme_os?.split(','),
        tool_libs: curScheme?.toollib_maps?.map((item: any) => item.toollib.id) ?? []
      })
    }
  }

  /**
   * 设置工具依赖表单初始值
   * @param schemeId 依赖方案 ID
   */
  const initFields = (schemeId: number) => {
    const arrs = find(toolSchemes, { id: schemeId })?.toollib_maps?.map((item: any, index: number) => ({
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

  const onFinish = () => {
    const formData = form.getFieldsValue();
    const params = {
      ...formData,
      condition: formData.condition || null,
      scheme_os: formData.scheme_os?.join(','),
      tool_libs: compact(formData.tool_libs)?.map((id: number) => ({ toollib: id })),
    };
    if (activeKey !== -1) {
      updateToolSchemes(orgSid, toolId, activeKey, params).then((res) => {
        getLibSchemes(res.id);
        message.success('依赖方案编辑成功');
      })
    } else {
      addToolSchemes(orgSid, toolId, params).then((res) => {
        getLibSchemes(res.id);
        message.success('依赖方案添加成功');
      })
    }
  }

  const onDelLibScheme = () => {
    if (activeKey === -1) { // 新增方案时
      setTabs([...dropRight(tabs)]);
    } else {
      delToolScheme(orgSid, toolId, activeKey).then(() => {
        message.success('依赖删除成功');
        getLibSchemes();
      })
    }
    setActiveKey(tabs[0])
  }

  if (!isEdit && isEmpty(toolSchemes)) {
    return null;
  }

  return (
    <Form
      {...layout}
      form={form}
      // 嵌套结构需要修改 Form 的 dom 类型
      component='div'
      name='libScheme'
    >
      <Form.Item label='依赖方案'>
        <div style={{ display: 'flex' }}>
          <div className={style.libSchemeTabs}>
            {
              tabs.map((id: number) => (
                <div
                  key={id}
                  className={style.schemeTabItem}
                  onClick={() => {
                    setActiveKey(id);
                  }}
                >
                  <span className={cn(style.itemContent, {
                    [style.active]: activeKey === id
                  })}>{id === -1 ? '添加依赖方案' : `方案ID: ${id}`}</span>
                </div>
              ))
            }
            {
              !tabs.includes(-1) && isEdit && (
                <div className={style.schemeTabItem}>
                  <Tooltip
                    title='添加方案'
                    getPopupContainer={() => document.body}
                  >
                    <PlusIcon
                      className={style.itemContent}
                      onClick={() => {
                        setTabs([...tabs, -1]);
                        setActiveKey(-1);
                      }}
                    />
                  </Tooltip>
                </div>
              )
            }
          </div>
        </div>
      </Form.Item>
      <div className={style.libScheme} >
        <Form.Item
          label="适用系统"
          name="scheme_os"
        >
          {
            getComponent(
              <Select mode='multiple'>
                {
                  Object.entries(LIB_ENV).map(([key, text]) => (
                    <Option key={key} value={key}>{text}</Option>
                  ))
                }
              </Select>,
              find(toolSchemes, { id: activeKey })?.scheme_os
            )
          }
        </Form.Item>
        <Form.Item
          label="判断条件"
          name="condition"
        >
          {
            getComponent(
              <TextArea rows={3} placeholder='仅支持=条件' />,
              find(toolSchemes, { id: activeKey })?.condition
            )
          }
        </Form.Item>
        <Form.Item label='工具依赖' {...layout} required>
          {
            isEdit ? fields.map((item, index) => {
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
                    <Select style={{ width: '440px' }}>
                      {
                        toolLibs.map((item) => (
                          <Option value={item.id} key={item.id}>{item.name}</Option>
                        ))
                      }
                    </Select>
                  </Form.Item>
                  <PlusIcon
                    className={style.addIcon}
                    onClick={() => {
                      add(index);
                    }}
                  />
                  {
                    fields.length > 1 && (
                      <TrashIcon
                        className={style.delIcon}
                        onClick={() => {
                          remove(index);
                        }}
                      />
                    )
                  }
                </Form.Item>
              )
            }) : (
              find(toolSchemes, { id: activeKey })?.toollib_maps?.map((item: any) => (
                <p key={item.id} style={{ marginBottom: '10px' }}>{item.toollib.name}</p>
              ))
            )
          }
        </Form.Item>
        <Form.Item label="" name="default_flag" valuePropName="checked">
          <Checkbox disabled={!isEdit}>默认方案</Checkbox>
        </Form.Item>
        {
          isEdit && (
            <Form.Item>
              <Button
                type='primary'
                htmlType='submit'
                key='edit'
                onClick={() => form
                  .validateFields()
                  .then(onFinish)
                }
              >{activeKey === -1 ? '新增' : '修改'}</Button>
              {
                activeKey === -1 ? (
                  <Button
                    className="ml-12"
                    onClick={() => {
                      form.resetFields();
                      setFields(defaultFields);
                    }}
                  >取消</Button>
                ) : (
                  <Button
                    className="ml-12"
                    danger
                    onClick={onDelLibScheme}
                  >删除</Button>
                )
              }
            </Form.Item>
          )
        }
      </div>
    </Form>
  )
}

export default LibScheme;