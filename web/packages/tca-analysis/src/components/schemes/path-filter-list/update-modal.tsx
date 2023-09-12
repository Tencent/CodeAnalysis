// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

/**
 * 添加/编辑过滤路径模态框
 */

import React, { useEffect } from 'react';

import { Input, Radio, Form, Dialog, Tooltip } from 'tdesign-react';
import { HelpCircleIcon } from 'tdesign-icons-react';

import style from './style.scss';
import { isEmpty } from 'lodash';

const { FormItem } = Form;

interface IProps {
  visible: boolean; // 模态框是否显示
  data: any; // 模态框数据
  onUpdateScanDir: (data: any) => void;
  onHideModal: () => void;
}

const initModalData = {
  scan_type: 2,
  path_type: 2,
};

const UpdateModal = (props: IProps) => {
  const { visible, data, onHideModal, onUpdateScanDir } = props;
  const [form] = Form.useForm();
  const isEdit = !isEmpty(data);

  useEffect(() => {
    if (visible) {
      form.setFieldsValue({ ...initModalData, ...data });
    } else {
      form.reset();
    }
  }, [visible, form, data]);

  /**
   * 表单保存操作
   * @param formData 参数
   */
  const onSubmitHandle = () => {
    form.validate().then((result: any) => {
      if (result === true) {
        onUpdateScanDir(form?.getFieldsValue(true));
      }
    });
  };

  return (
    <Dialog
      header={`${isEdit ? '编辑' : '添加'}路径过滤`}
      visible={visible}
      onCancel={onHideModal}
      onClose={onHideModal}
      width={520}
      className={style.addPathModal}
      confirmBtn={isEdit ? '确定' : '添加'}
      onConfirm={onSubmitHandle}
    >
      <Form
        labelAlign='left'
        labelWidth={120}
        className={style.form}
        form={form}
        initialData={data}
      >
        <FormItem
          label="路径类型"
          name="path_type"
          rules={[{ required: true, message: '请选择路径类型' }]}
        >
          <Radio.Group>
            <Radio value={2}>
              正则表达式
              <Tooltip
                overlayClassName={style.descTooltip}
                content={
                  <ul>
                    <li>请填写相对路径(基于代码库根目录)，要求匹配到文件</li>
                    <li>
                      使用Unix通配符格式，示例如下：
                      <ul>
                        <li>代码根目录</li>
                        <li>|-src</li>
                        <li style={{ paddingLeft: 20 }}>|- test</li>
                        <li style={{ paddingLeft: 40 }}>|- main_test.py</li>
                        <li style={{ paddingLeft: 40 }}>|- input_test.py</li>
                        <li style={{ paddingLeft: 20 }}>|- main.py</li>
                        <li>|-test</li>
                        <li style={{ paddingLeft: 20 }}>|- param_test.py</li>
                        <li>匹配src/test目录：src/test/.*</li>
                        <li>匹配根目录下的test目录：test/.*</li>
                        <li>匹配所有_test.py后缀的文件：.*_test\.py</li>
                      </ul>
                    </li>
                    <li>修改后，下次分析生效，需要启动一次全量分析处理历史存量问题</li>
                  </ul>
                }
              >
                <HelpCircleIcon className={style.questionIcon} />
              </Tooltip>
            </Radio>
            <Radio value={1}>
              通配符
              <Tooltip
                overlayClassName={style.descTooltip}
                content={
                  <ul className={style.descContent}>
                    <li>请填写相对路径(基于代码库根目录)，要求匹配到文件</li>
                    <li>
                      使用Unix通配符格式，示例如下：
                      <ul>
                        <li>代码根目录</li>
                        <li>|-src</li>
                        <li style={{ paddingLeft: 20 }}>|- test</li>
                        <li style={{ paddingLeft: 40 }}>|- main_test.py</li>
                        <li style={{ paddingLeft: 40 }}>|- input_test.py</li>
                        <li style={{ paddingLeft: 20 }}>|- main.py</li>
                        <li>|-test</li>
                        <li style={{ paddingLeft: 20 }}>|- param_test.py</li>
                        <li>匹配src/test目录：src/test/*</li>
                        <li>匹配根目录下的test目录：test/*</li>
                        <li>匹配所有_test.py后缀的文件：*_test.py</li>
                      </ul>
                    </li>
                    <li>修改后，下次分析生效，需要启动一次全量分析处理历史存量问题</li>
                  </ul>
                }
              >
                <HelpCircleIcon className={style.questionIcon} />
              </Tooltip>
            </Radio>
          </Radio.Group>
        </FormItem>
        <FormItem
          label="目录/文件路径"
          name="dir_path"
          rules={[{ required: true, message: '请输入目录/文件路径' }]}
        >
          <Input placeholder="请输入路径" />
        </FormItem>
        <FormItem
          shouldUpdate={(prevValues: any, curValues: any) => prevValues.path_type !== curValues.path_type
          }
        >
          {({ getFieldValue }: { getFieldValue: any }) => (
            <FormItem
              label="过滤类型"
              name="scan_type"
              rules={[{ required: true, message: '请选择过滤类型' }]}
              style={{ marginBottom: 0 }}
            >
              <Radio.Group>
                <Radio value={1}>
                  include（包含）
                  <Tooltip
                    overlayClassName={style.descTooltip}
                    content={`表示只分析，如只分析 src/ 目录：src/${getFieldValue('path_type') === 1 ? '' : '.'
                    }*`}
                  >
                    <HelpCircleIcon className={style.questionIcon} />
                  </Tooltip>
                </Radio>
                <Radio value={2}>
                  exclude（过滤）
                  <Tooltip
                    overlayClassName={style.descTooltip}
                    content={`表示只屏蔽，如要屏蔽 src/lib/ 目录：src/lib/${getFieldValue('path_type') === 1 ? '' : '.'
                    }*`}
                  >
                    <HelpCircleIcon className={style.questionIcon} />
                  </Tooltip>
                </Radio>
              </Radio.Group>
            </FormItem>
          )}
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default UpdateModal;
