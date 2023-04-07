import React, { useRef } from 'react';
import { t } from '@src/utils/i18n';
import { Dialog, Form, message, Input, FormInstanceFunctions } from 'tdesign-react';

// 项目内
import { jobAPI } from '@src/services/jobs';
import { JobData } from './types';

const { FormItem } = Form;

interface CancelJobModalProps {
  visible: boolean;
  onOk: () => void;
  onCancel: () => void;
  jobInfo: JobData;
}

const CancelJobModal = ({ jobInfo, visible, onOk, onCancel }: CancelJobModalProps) => {
  const formRef = useRef<FormInstanceFunctions>(null);

  /**
   * 表单保存操作
   */
  const onSubmitHandle = () => {
    formRef.current?.validate().then((result) => {
      if (result === true) {
        const fieldsValue = formRef.current?.getFieldsValue(true);
        jobAPI.cancel(jobInfo.id, fieldsValue).then(() => {
          message.success(t('取消任务成功'));
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
      header={t('取消任务')}
      visible={visible}
      onConfirm={onSubmitHandle}
      onClose={onCancel}
      onOpened={onReset}
      onClosed={onReset}
    >
      <Form
        layout='vertical'
        ref={formRef}
      >
        <FormItem
          name="remarks"
          label={t('取消原因')}
          rules={[{ required: true, message: t('取消原因为必选项') }]}
        >
          <Input />
        </FormItem>
      </Form>
    </Dialog>
  );
};

export default CancelJobModal;
