import React, { useRef } from 'react';
import { useTranslation } from 'react-i18next';
import { Dialog, Form, message, Select, FormInstanceFunctions } from 'tdesign-react';

// 项目内
import { putToolOpen } from '@src/services/tools';

// 模块内
import { PermEnum, PERM_OPTIONS } from './constants';
import { ToolData } from './types';

const { FormItem } = Form;
// const { Option } = Select;

/** 获取权限状态 */
const getPermStatus = (tool: ToolData) => {
  if (tool) {
    if (tool.open_maintain) {
      return PermEnum.ALL_CUSTOM;
    }
    if (tool.open_user) {
      return PermEnum.ALL;
    }
  }
  return PermEnum.TEAM;
};

/** 根据perm_status获取open_user、 open_maintain参数 */
const getParamsByPermStatus = (formData: any) => {
  let openUser = false;
  let openMaintain = false;
  if (formData.perm_status === PermEnum.ALL_CUSTOM) {
    openUser = true;
    openMaintain = true;
  } else if (formData.perm_status === PermEnum.ALL) {
    openUser = true;
    openMaintain = false;
  }
  return { open_user: openUser, open_maintain: openMaintain };
};

interface ToolPermModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  toolinfo: ToolData | null;
}

const ToolPermModal = ({ toolinfo, visible, onOk, onCancel }: ToolPermModalProps) => {
  const formRef = useRef<FormInstanceFunctions>(null);
  const { t } = useTranslation();

  /** 表单保存操作 */
  const onConfirm = () => {
    formRef.current?.validate().then((result: any) => {
      if (result === true && toolinfo) {
        const formData = formRef.current?.getFieldsValue(true);
        putToolOpen(toolinfo.id, getParamsByPermStatus(formData)).then(() => {
          message.success(t('已调整工具权限'));
          onOk();
        });
      }
    });
  };

  /** 重置表单操作 */
  const onReset = () => {
    formRef.current?.reset();
  };

  return (
    <Dialog
      header={t('调整工具权限')}
      visible={visible}
      onConfirm={onConfirm}
      onClose={onCancel}
      onOpened={onReset}
      onClosed={onReset}
    >
      <Form
        layout='vertical'
        ref={formRef}
        resetType='initial'
      >
        <FormItem
          label={t('工具权限')}
          name="perm_status"
          initialData={getPermStatus(toolinfo)}
          help={<>
            <p>团队内可用：即工具团队白名单内团队可用；</p>
            <p>全平台可用：即不同团队都可见可用；</p>
            <p>支持自定义规则，全平台可用：即该工具允许用户添加自定义规则，此类工具不同团队都可见可用。</p>
          </>}
        >
          <Select options={PERM_OPTIONS} />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default ToolPermModal;
