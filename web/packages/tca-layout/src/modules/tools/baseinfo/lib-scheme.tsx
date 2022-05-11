/**
 * 依赖方案
 */
import React, { useEffect, useState } from 'react';
import cn from 'classnames';
import { isEmpty, find, dropRight, compact } from 'lodash';

import { Form, Select, Input, Checkbox, Tooltip, Button, message } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';

import { getToolLibs, getToolSchemes, addToolSchemes, delToolScheme } from '@src/services/tools';
import { LIB_ENV } from '@src/modules/tool-libs/constants';

import style from '../detail.scss';

const { Option } = Select;
const { TextArea } = Input;

interface LibSchemeProps {
  layout: any;
  orgSid: string;
  toolId: number;
}

const defaultFields = [{
  name: 0,  // 字段顺序
  key: 0  // react key，不随顺序更改
}];

const LibScheme = (props: LibSchemeProps) => {
  const [form] = Form.useForm();
  const { layout, orgSid, toolId } = props;
  const [toolSchemes, setToolSchemes] = useState([]);
  const [toolLibs, setToolLibs] = useState<Array<any>>([]);
  const [activeKey, setActiveKey] = useState(toolSchemes?.[0]?.id);
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
    console.log('activeKey', activeKey)
    if (activeKey) {
      initFields(activeKey);
      form.resetFields();
    }
  }, [activeKey])

  const getLibSchemes = (activeKey?: number) => {
    getToolSchemes(orgSid, toolId).then((res) => {
      setToolSchemes(res);
      initTabs(res, activeKey);
    })
  }

  const initTabs = (toolSchemes: any, activeKey?: number) => {
    if (!isEmpty(toolSchemes)) {
      const ids = toolSchemes.map((item: any) => item.id);
      setTabs(ids);
      setActiveKey(activeKey || ids[0]);
    }
  }
  /**
   * 设置工具依赖表单初始值
   * @param schemeId 依赖方案 ID
   */
  const initFields = (schemeId: number) => {
    const arrs = find(toolSchemes, { id: schemeId })?.toollib_maps?.map((item: any, index: number) => ({
      name: index,
      key: item.id
    })) ?? defaultFields;

    console.log(find(toolSchemes, { id: schemeId })?.toollib_maps?.map((item: any) => item.toollib.id))
    console.log(arrs)

    if (!isEmpty(arrs)) {
      setFields(arrs);
    }
  }

  // console.log(toolSchemes)

  const add = (index: number) => {
    const arrs = fields;

    if (index >= 0 && index <= arrs.length) {
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
    // 因为key不重复，移除操作会导致表单获取的数据为空，表单提交需注意清理数据
    setFields(
      [...fields.filter((item) => item.name !== index)]
    )
  }

  const onFinish = (formData: any) => {
    console.log('formData', formData)
    addToolSchemes(orgSid, toolId, {
      tool_libs: compact(formData.tool_libs)?.map((id: number) => ({ toollib: id })),
      // condition: null
    }).then((res) => {
      getLibSchemes(res.id);
      message.success('依赖方案添加成功');
      console.log(res)
    })
  }

  const onDelLibScheme = () => {
    if (activeKey === -1) { // 新增方案时
      setTabs([...dropRight(tabs)]);
    } else {
      delToolScheme(orgSid, toolId, activeKey).then((res) => {
        console.log(res);
        message.success('依赖删除成功');
        getLibSchemes();
      })
    }

    setActiveKey(tabs[0])
  }

  // console.log(activeKey)

  return (
    <Form
      {...layout}
      form={form}
      name='libScheme'
      initialValues={{
        ...toolSchemes[activeKey],
        tool_libs: find(toolSchemes, { id: activeKey })?.toollib_maps?.map((item: any) => item.toollib.id) ?? []
        // tool_libs: [4, 3]
      }}
      onFinish={onFinish}
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
                    // form.resetFields();
                  }}
                >
                  <span className={cn(style.itemContent, {
                    [style.active]: activeKey === id
                  })}>{id === -1 ? '添加依赖方案' : `方案${id}`}</span>
                </div>
              ))
            }
            {
              !tabs.includes(-1) && (
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
                    name={['tool_libs', item.key]}
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
            })
          }
        </Form.Item>
        <Form.Item label="" name="default_flag" valuePropName="checked">
          <Checkbox >默认方案</Checkbox>
        </Form.Item>
        <Form.Item>
          <Button
            type='primary'
            htmlType='submit'
            key='edit'
          >{activeKey === -1 ? '新增' : '编辑'}</Button>
          <Button
            className="ml-12"
            danger
            onClick={onDelLibScheme}
          >删除</Button>
        </Form.Item>
      </div>
    </Form>
  )
}

export default LibScheme;