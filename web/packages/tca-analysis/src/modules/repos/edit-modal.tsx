/**
 * 编辑仓库信息
 */
import React, { useEffect, useState } from 'react';
import { Modal, Form, Input, Space, Button, message } from 'coding-oa-uikit';
import { getRepoName } from '@tencent/micro-frontend-shared/tca/util';
import { useLoginUserIsAdmin } from '@plat/hooks';
import { putRepo, getRepoMembers, delRepo } from '@src/services/repos';

interface EditModalProps {
  orgSid: string;
  teamName: string;
  visible: boolean;
  repoInfo: any;
  onCancel: () => void;
  callback: (deletedRepo: boolean) => void;
}

const EditModal = (props: EditModalProps) => {
  const { orgSid, teamName, visible, repoInfo, onCancel, callback } = props;
  const [form] = Form.useForm();
  const [admins, setAdmins] = useState<string[]>([]);
  const isAdmin = useLoginUserIsAdmin(admins);

  useEffect(() => {
    if (visible) {
      form.resetFields();
      getRepoMembers(orgSid, teamName, repoInfo.id).then((res: any) => {
        setAdmins(res.admins?.map((userinfo: any) => userinfo.username) || []);
      });
    }
  }, [visible]);

  const onConfirm = () => {
    form.validateFields().then((formData) => {
      putRepo(orgSid, teamName, repoInfo.id, {
        ...repoInfo,
        ...formData,
      }).then(() => {
        message.success('修改成功');
        callback?.(false);
        onCancel();
      });
    });
  };

  const onDel = () => {
    Modal.confirm({
      title: `是否确认删除代码库【${getRepoName(repoInfo)}】？`,
      onOk() {
        delRepo(orgSid, teamName, repoInfo.id).then(() => {
          message.success('已删除代码库');
          callback?.(true);
          onCancel();
        });
      },
    });
  };

  return (
    <Modal
      title="仓库设置"
      visible={visible}
      onCancel={onCancel}
      footer={(
        <Space>
          <Button onClick={onCancel}>取消</Button>
          <Button type='primary' onClick={onConfirm}>确认</Button>
          {
            isAdmin && (
              <Button danger type='primary' onClick={onDel}>删除仓库</Button>
            )
          }
        </Space>
      )}
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={repoInfo && {
          ...repoInfo,
          name: getRepoName(repoInfo),
        }}
      >
        <Form.Item
          name="name"
          label='代码库别名'
        >
          <Input placeholder='代码库别名' />
        </Form.Item>
        <Form.Item
          name="ssh_url"
          label='ssh 地址'
        >
          <Input placeholder='ssh 地址' />
        </Form.Item>
      </Form>
    </Modal>
  );
};

export default EditModal;
