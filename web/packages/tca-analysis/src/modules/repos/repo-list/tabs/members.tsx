// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { unionWith, isEqual } from 'lodash';
import { Row, Col, Button, Avatar, Modal, Select, message } from 'coding-oa-uikit';
import PlusCircleIcon from 'coding-oa-uikit/lib/icon/PlusCircle';
import UserIcon from 'coding-oa-uikit/lib/icon/User';

// 项目内
import { useStateStore, useDispatchStore } from '@src/context/store';
import { SET_CUR_REPO_MEMBER } from '@src/context/constant';
import { getUserImgUrl } from '@src/utils';
import { getMembers } from '@src/services/common';
import { postRepoMembers } from '@src/services/repos';

// 模块内
import s from '../style.scss';

const PERM_ENUM = {
  ADMIN: 1,
  USER: 2,
};

interface IMemberItem {
  list: Array<any>;
  title: string;
  onAddMemberClick: () => void;
}

const MemberItem = ({ list, title, onAddMemberClick }: IMemberItem) => (
    <div className={s.memberItem}>
        <div className={s.tit}>{title}</div>
        <Row gutter={[16, 16]} align="middle" className={s.group}>
            <Col xl={6} lg={8} md={12} sm={24} key="add-member">
                <Button type="link" icon={<PlusCircleIcon />} onClick={onAddMemberClick}>
                    添加成员
                </Button>
            </Col>
            {list.map((userinfo: any) => (
                <Col xl={6} lg={8} md={12} sm={24} key={userinfo.username}>
                    <Avatar
                        size="small"
                        src={userinfo.avatar_url || getUserImgUrl(userinfo.username)}
                        alt={userinfo.nickname}
                        icon={<UserIcon />}
                    />
                    <span className=" inline-block vertical-middle ml-sm">{userinfo.nickname}</span>
                </Col>
            ))}
        </Row>
    </div>
);

interface IProps {
  orgSid: string;
  teamName: string;
  repoId: any;
  admins: Array<any>;
  users: Array<any>;
}

const Members = ({ orgSid, teamName, repoId, admins }: IProps) => {
  const dispatch = useDispatchStore();
  const { t } = useTranslation();
  const [inviteVisb, setInviteVisb] = useState(false);
  const { projectMembers } = useStateStore();
  const userOptions = unionWith(projectMembers.admins, projectMembers.users, isEqual).map(user => ({
    ...user,
    label: user.nickname,
    value: user.username,
  }));

  const [form, setForm] = useState({
    role: PERM_ENUM.USER,
    users: [],
  });

  const onAddMemberHandle = (role: number) => {
    setForm({
      ...form,
      role,
    });
    setInviteVisb(true);
  };

  const onSelectUsersHandle = (value: any) => {
    setForm({
      ...form,
      users: value,
    });
  };

  const onOkHandle = () => {
    if (form.users.length > 0) {
      postRepoMembers(orgSid, teamName, repoId, form).then(() => {
        message.success(t('成员添加成功'));
        // 获取代码库成员
        getMembers(orgSid, teamName, repoId).then((response) => {
          dispatch({
            type: SET_CUR_REPO_MEMBER,
            payload: response,
          });
        });
        setInviteVisb(false);
      });
    } else {
      message.warning(t('成员为必选项'));
    }
  };

  return (
        <div style={{ paddingTop: '30px' }}>
            <Modal
                title={t('添加成员')}
                visible={inviteVisb}
                onOk={onOkHandle}
                onCancel={() => setInviteVisb(false)}
            >
                <Select
                    mode="multiple"
                    placeholder={t('团队成员，可多选')}
                    showSearch
                    value={form.users}
                    style={{ width: '100%' }}
                    options={userOptions}
                    onChange={onSelectUsersHandle}
                />
            </Modal>
            <MemberItem
                list={admins}
                title={t('管理员')}
                onAddMemberClick={() => onAddMemberHandle(PERM_ENUM.ADMIN)}
            />
            {/* <MemberItem
                list={users}
                title={t('普通成员')}
                onAddMemberClick={() => onAddMemberHandle(1)}
            /> */}
        </div>
  );
};
export default Members;
