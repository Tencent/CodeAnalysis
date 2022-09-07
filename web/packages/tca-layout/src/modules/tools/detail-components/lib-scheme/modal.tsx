/**
 * 新增/编辑弹框
 */
import React, { useState, useEffect, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import cn from 'classnames';
import { isEmpty, compact } from 'lodash';
import { Modal, Form, Select, Input, Tag, Tooltip, message, Checkbox } from 'coding-oa-uikit';
import PlusIcon from 'coding-oa-uikit/lib/icon/Plus';
import TrashIcon from 'coding-oa-uikit/lib/icon/Trash';

import { LIB_ENV, LibTypeEnum, LIB_TYPE } from '@src/constant';
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
  key: 0,  // react key，不随顺序更改
}];

interface UpdateLibSchemeModalProps {
  orgSid: string;
  toolId: number;
  visible: boolean;
  initData: any;
  toolSchemes: any;
  onClose: () => void;
  callback: () => void;
}

const UpdateLibSchemeModal = (props: UpdateLibSchemeModalProps) => {
  const { orgSid, toolId, visible, initData, toolSchemes, onClose, callback } = props;
  const { t } = useTranslation();
  const [form] = Form.useForm();
  const [toolLibs, setToolLibs] = useState<Array<any>>([]);
  const [fields, setFields] = useState<Array<any>>(defaultFields);
  const [maxFieldKey, setMaxFieldKey] = useState<number>(0);  // tool_libs max key
  const isEdit = initData && !isEmpty(initData);

  const isOnlyDefault = useMemo(() => {  // 仅有一个默认方案时，不允许取消操作
    const defaultScheme = toolSchemes.filter((item: any) => item.default_flag);
    return defaultScheme.length === 1 && defaultScheme?.[0]?.id === initData?.id;
  }, [toolSchemes, initData]);

  useEffect(() => {
    if (visible) {
      initFields();
      if (isEdit) {  // 编辑
        getLibs({ os: initData?.os?.join(',') });
        form.setFieldsValue({
          ...initData,
          scheme_os: initData?.scheme_os?.split(';'),
          tool_libs: initData?.toollib_maps?.map((item: any) => item.toollib.id) ?? [],
        });
      } else {  // 新增
        setToolLibs([]);
        form.resetFields();
      }
    }
  }, [visible]);

  useEffect(() => getLibs(), [orgSid]);

  const getLibs = (params = {}) => {
    getToolLibs(orgSid, {
      ...params,
      offset: 0,
      limit: 100,
    }).then((res: any) => {
      setToolLibs(res.results);
    });
  };

  /**
  * 设置工具依赖表单初始值
  */
  const initFields = () => {
    const arrs = initData?.toollib_maps?.map((item: any, index: number) => ({
      name: index,
      key: index,
    })) ?? defaultFields;

    if (!isEmpty(arrs)) {
      setFields(arrs);
      setMaxFieldKey(arrs.length - 1);
    }
  };

  const add = (index: number) => {
    const arrs = fields;

    if (index >= 0 && index <= arrs.length) {
      const values = form.getFieldValue('tool_libs') || [];
      form.setFieldsValue({
        tool_libs: [
          ...values.slice(0, index + 1),
          undefined,
          ...values.slice(index + 1),
        ],
      });
      setFields([
        ...arrs.slice(0, index + 1),
        {
          name: index + 1,
          key: maxFieldKey + 1,
        },
        ...arrs.slice(index + 1).map((item: any) => ({
          ...item,
          name: item.name + 1,
        })),
      ]);

      setMaxFieldKey(maxFieldKey + 1);
    }
  };

  const remove = (index: number) => {
    const values = form.getFieldValue('tool_libs');
    const arrs = fields;

    values.splice(index, 1);
    form.setFieldsValue({ tool_libs: values });

    setFields([
      ...arrs.slice(0, index),
      ...arrs.slice(index + 1).map((item: any) => ({
        ...item,
        name: item.name - 1,
      })),
    ]);
  };

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
        message.success(t('依赖方案编辑成功'));
        onClose();
      });
    } else {
      addToolSchemes(orgSid, toolId, params).then(() => {
        message.success(t('依赖方案添加成功'));
        callback();
        onClose();
      });
    }
  };

  /** 表单保存操作 */
  const onSubmitHandle = () => {
    form.validateFields().then(onFinish);
  };

  return (
    <Modal
      title={`${isEdit ? t('编辑') : t('添加')}${t('依赖配置')}`}
      width={610}
      visible={visible}
      className={style.updateSchemeModal}
      afterClose={form.resetFields}
      onCancel={onClose}
      onOk={onSubmitHandle}
    >
      <Form {...layout} form={form}>
        <Form.Item
          label={t('判断条件')}
          name="condition"
        >
          <TextArea
            rows={4}
            placeholder={t('当环境变量满足该条件时使用当前依赖，如果不需要区分，可以不填。示例：设置判断条件PYTHON_VERSION=3时，使用python3依赖。')} />
        </Form.Item>
        <Form.Item
          label={t('适用系统')}
          name="scheme_os"
        >
          <Select
            mode='multiple'
            placeholder={t('选择当前方案适用的操作系统')}
            onChange={(values: Array<string>) => {
              getLibs({ os: values?.join(',') });
            }}>
            {
              Object.entries(LIB_ENV).map(([key, text]) => (
                <Option key={key} value={key}>{text}</Option>
              ))
            }
          </Select>
        </Form.Item>
        <Form.Item label={t('工具依赖')} {...layout} required>
          {
            fields.map((item, index) => (
              <Form.Item key={item.key}>
                <Form.Item
                  {...item}
                  rules={[{
                    required: true,
                    message: t('请选择工具依赖'),
                  }]}
                  name={['tool_libs', item.name]}
                  noStyle
                >
                  <Select
                    showSearch
                    optionFilterProp="label"
                    style={{ width: '400px' }}
                    optionLabelProp="label"
                    placeholder={t('选择当前方案需要加载的工具依赖')}
                    notFoundContent={isEmpty(form.getFieldValue('scheme_os')) ? t('请先选择适用系统') : t('暂无数据')}
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
                <Tooltip title={t('添加')} getPopupContainer={() => document.body}>
                  <PlusIcon
                    className={style.addIcon}
                    onClick={() => {
                      add(index);
                    }}
                  />
                </Tooltip>
                {
                  fields.length > 1 && (
                    <Tooltip title={t('删除')} getPopupContainer={() => document.body}>
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
            ))
          }
        </Form.Item>
        <Form.Item
          label=""
          {...layout}
          name="default_flag"
          valuePropName="checked"
        >
          <Checkbox disabled={isOnlyDefault}>{t('默认方案')}</Checkbox>
        </Form.Item>
        {
          isOnlyDefault && (
            <div className={style.defaultDesc}>{t('必须有一个默认方案，可设置其他方案为默认方案来切换默认方案')}</div>
          )
        }
      </Form>
    </Modal>
  );
};

export default UpdateLibSchemeModal;
