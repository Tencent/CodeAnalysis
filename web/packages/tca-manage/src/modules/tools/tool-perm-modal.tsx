import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Modal, Form, message, Radio } from 'coding-oa-uikit';

// 项目内
import { putToolOpen } from '@src/services/tools';

// 模块内
import { PERM_ENUM, PERM_OPTIONS } from './constants';

interface IProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  toolinfo: any;
}

const ToolPermModal = ({ toolinfo, visible, onOk, onCancel }: IProps) => {
  const [form] = Form.useForm();
  const { t } = useTranslation();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const getParamsByPermStatus = (formData: any) => {
    let openUser = false;
    let openMaintain = false;
    if (formData.perm_status === PERM_ENUM.ALL_CUSTOM) {
      openUser = true;
      openMaintain = true;
    } else if (formData.perm_status === PERM_ENUM.ALL) {
      openUser = true;
      openMaintain = false;
    }
    return { open_user: openUser, open_maintain: openMaintain };
  };

  /**
     * 表单保存操作
     * @param formData 参数
     */
  const onSubmitHandle = () => {
    form.validateFields().then((formData) => {
      if (toolinfo) {
        putToolOpen(toolinfo.id, getParamsByPermStatus(formData)).then(() => {
          message.success(t('已调整工具权限'));
          onOk();
        });
      }
    });
  };

  const getPermStatus = (tool: any) => {
    if (tool) {
      if (tool.open_maintain) {
        return PERM_ENUM.ALL_CUSTOM;
      }
      if (tool.open_user) {
        return PERM_ENUM.ALL;
      }
    }
    return PERM_ENUM.TEAM;
  };

  return (
    <Modal
      forceRender
      title={t('调整工具权限')}
      visible={visible}
      onOk={onSubmitHandle}
      onCancel={onCancel}
      afterClose={form.resetFields}
    >
      <Form
        layout={'vertical'}
        form={form}
        initialValues={{
          perm_status: getPermStatus(toolinfo),
        }}
      >
        <Form.Item
          name="perm_status"
          rules={[{ required: true, message: t('负责人为必填项') }]}
        >
          <Radio.Group size="small">
            {PERM_OPTIONS.map(item => (
              <Radio key={item.value} value={item.value} className="block mb-md">
                {item.label}
              </Radio>
            ))}
          </Radio.Group>
        </Form.Item>
        <div className=" text-grey-7 fs-12">
          注：团队内可用：即工具配置了可用团队白名单的团队可用，默认创建工具的团队已在白名单内；全平台可用：即不同团队都可见可用；支持自定义规则，全平台可用：即该工具支持用户添加自定义规则，此类工具不同团队都可见可用。
        </div>
      </Form>
    </Modal>
  );
};

export default ToolPermModal;
