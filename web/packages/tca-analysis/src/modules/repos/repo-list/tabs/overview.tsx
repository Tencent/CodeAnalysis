// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { Form, Input, Button, message, Avatar } from 'coding-oa-uikit';
import UserIcon from 'coding-oa-uikit/lib/icon/User';
import { merge } from 'lodash';
// 项目内
import { t } from '@src/i18n/i18next';
import { formatDateTime, getUserImgUrl } from '@src/utils';
import { putRepo } from '@src/services/repos';
import { useDispatchStore } from '@src/context/store';
import { SET_CUR_REPO } from '@src/context/constant';

interface IProps {
  curRepo: any;
  orgSid: string;
  teamName: string;
  repoId: number;
  deletable: boolean;
  onDelete: () => void;
}

const layout = {
  labelCol: { span: 4 },
};

const Overview = ({ curRepo, orgSid, teamName, repoId, deletable, onDelete }: IProps) => {
  const [form] = Form.useForm();
  const [edit, setEdit] = useState(false);
  const dispatch = useDispatchStore();
  const creatorInfo = curRepo.creator || {};

  // 重置
  const onReset = () => {
    setEdit(false);
    form.resetFields();
  };

  const onFinish = (name: string) => {
    putRepo(orgSid, teamName, repoId, merge(curRepo, { name })).then((response) => {
      message.success('仓库信息已更新');
      onReset();
      dispatch({
        type: SET_CUR_REPO,
        payload: response,
      });
    });
  };

  return (
    <Form
      {...layout}
      initialValues={curRepo || {}}
      form={form}
      style={{ width: '530px', marginTop: '30px' }}
      onFinish={values => onFinish(values.name)}
    >
      <Form.Item label={t('仓库地址')} name="scm_url">
        <span style={{ wordBreak: 'break-all' }}>{curRepo.scm_url}</span>
      </Form.Item>
      <Form.Item
        label={t('仓库别名')}
        name="name"
        rules={edit ? [{ required: true, message: t('仓库别名为必填项') }] : undefined}
      >
        {edit ? <Input width={400} /> : <span>{curRepo.name}</span>}
      </Form.Item>
      <Form.Item label={t('创建人')} name="creator">
        <>
          <Avatar
            size="small"
            src={creatorInfo.avatar_url || getUserImgUrl(creatorInfo.nickname)}
            alt={creatorInfo.nickname}
            icon={<UserIcon />}
          />
          <span className=" inline-block vertical-middle ml-sm">
            {creatorInfo.nickname}
          </span>
        </>
      </Form.Item>

      <Form.Item label={t('创建时间')} name="created_time">
        <span>{formatDateTime(curRepo.created_time)}</span>
      </Form.Item>

      <div style={{ marginTop: '30px' }}>
        {edit ? (
          <>
            <Button type="primary" htmlType="submit" key="submit">
              {t('确定')}
            </Button>
            <Button className=" ml-12" htmlType="button" onClick={onReset}>
              {t('取消')}
            </Button>
          </>
        ) : (
          <Button
            key="edit"
            htmlType="button"
            type="primary"
            onClick={() => setEdit(true)}
          >
            {t('编辑')}
          </Button>
        )}
        {deletable && <Button className=" ml-12" htmlType="button" onClick={onDelete} danger type='primary'>
          {t('删除代码库')}
        </Button>}
      </div>
    </Form>
  );
};
export default Overview;
