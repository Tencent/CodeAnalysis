import React, { useState, useEffect } from 'react';
import { t } from '@src/utils/i18n';
import { Modal, Form, Input, message } from 'coding-oa-uikit';

// 项目内
import { createTeam, updateTeamInfo } from '@src/services/team';
import { getExtraCreateTeamInfos } from '@plat/modules/team';

interface TeamModalProps {
  visible: boolean;
  data: any;
  onOk: () => void;
  onCancel: () => void;
}

const TeamModal = ({ visible, data, onOk, onCancel }: TeamModalProps) => {
  const [loading, setLoading] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.resetFields();
    }
  }, [visible]);

  const onFinish = (formData: any) => {
    setLoading(true);
    const promise = data ? updateTeamInfo(data.org_sid, formData) : createTeam(formData);
    promise
      .then(() => {
        message.success(`已${data ? '更新团队信息' : '创建团队'}`);
        onOk();
      })
      .finally(() => {
        setLoading(false);
      });
  };

  return (
    <Modal
      title={data ? t('更新团队信息') : t('创建团队')}
      width={480}
      visible={visible}
      onCancel={onCancel}
      afterClose={form.resetFields}
      okButtonProps={{
        loading,
      }}
      onOk={() => {
        form.validateFields().then(onFinish);
      }}
    >
      <Form layout="vertical" form={form} initialValues={data}>
        <Form.Item
          name="name"
          label={t('团队名称')}
          rules={[{ required: true, message: t('团队名称为必填项') }]}
        >
          <Input placeholder="例如：腾讯科技" />
        </Form.Item>
        <Form.Item
          name="owner"
          label={t('团队负责人')}
          rules={[{ required: true, message: t('负责人为必填项') }]}
        >
          <Input placeholder='请输入负责人贵姓' />
        </Form.Item>
        <Form.Item
          name="tel_number"
          label="微信关联手机号"
          rules={[
            {
              required: true,
              message: t('微信关联的手机号为必填项'),
            },
            {
              pattern: /^[0-9,-]*$/,
              message: t('请输入合法的手机号'),
            },
          ]}
        >
          <Input placeholder='请输入微信关联手机号' />
        </Form.Item>
        {getExtraCreateTeamInfos?.()}
      </Form>
    </Modal>
  );
};

export default TeamModal;
