// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { t } from '@src/utils/i18n';
import { Button, Avatar, Row, Col, Modal, Select, message } from 'coding-oa-uikit';
import PlusCircleIcon from 'coding-oa-uikit/lib/icon/PlusCircle';
import UserIcon from 'coding-oa-uikit/lib/icon/User';
import CloseCircleIcon from 'coding-oa-uikit/lib/icon/CloseCircle';
import { unionWith, isEqual } from 'lodash';

// 项目内
import { getUserImgUrl } from '@src/utils';
import PageHeader from '@tencent/micro-frontend-shared/tdesign-component/page-header';
import { getTeamMemberRouter } from '@src/utils/getRoutePath';

// 模块内
import {
  getProjectTeamMembers,
  postProjectTeamMembers,
  getOrgMembers,
  delProjectTeamMember,
} from '@src/services/common';
import s from '../style.scss';

const PERM_ENUM = {
  ADMIN: 1,
  USER: 2,
};

const PERM_CHOICES = {
  [PERM_ENUM.ADMIN]: {
    tit: '管理员',
    desc: '（具备项目内全部查看、操作权限）',
  },
  [PERM_ENUM.USER]: {
    tit: '普通成员',
    desc: '（具备项目内查看、登记代码库、启动分析任务等相关权限）',
  },
};

interface IMemberItem {
  role: number;
  list: Array<any>;
  onAddMemberClick: (role: number) => void;
  onRemoveMemberClick: (role: number, userinfo: any) => void;
}

const MemberItem = ({ list, role, onAddMemberClick, onRemoveMemberClick }: IMemberItem) => (
    <div className={s.memberItem}>
        <div className={s.tit}>
            {PERM_CHOICES[role].tit}
            <small className=" text-grey-7">{PERM_CHOICES[role].desc}</small>
        </div>
        <Row gutter={[16, 16]} align="middle" className={s.group}>
            <Col xl={6} lg={8} md={12} sm={24}>
                <Button
                    type="link"
                    icon={<PlusCircleIcon />}
                    onClick={() => onAddMemberClick(role)}
                >
                    添加成员
                </Button>
            </Col>
            {list.map((userinfo: any) => (
                <Col xl={6} lg={8} md={12} sm={24} key={userinfo.username}>
                    <Avatar
                        size="small"
                        src={getUserImgUrl(userinfo.username)}
                        alt={userinfo.nickname}
                        icon={<UserIcon />}
                    />
                    <span className="ml-sm mr-xs">{userinfo.nickname}</span>
                    <Button
                        type="text"
                        icon={<CloseCircleIcon />}
                        size="small"
                        onClick={() => onRemoveMemberClick(role, userinfo)}
                    />
                </Col>
            ))}
        </Row>
    </div>
);

const Group = () => {
  const { orgSid, teamName }: any = useParams();
  const [allUsers, setAllUsers] = useState<Array<any>>([]);

  const [members, setMembers] = useState<any>({
    admins: [],
    users: [],
  });
  const userOptions = allUsers.map(user => ({
    ...user,
    label: user.nickname,
    value: user.username,
  }));
  const [inviteVisb, setInviteVisb] = useState(false);
  const [form, setForm] = useState({
    role: PERM_ENUM.USER,
    users: [],
  });

  const getTeamUsers = () => {
    getProjectTeamMembers(orgSid, teamName).then((response: any) => {
      setMembers(response);
    });
  };

  useEffect(() => {
    getOrgMembers(orgSid).then((response) => {
      setAllUsers(unionWith(response.admins, response.users, isEqual));
    });
    getTeamUsers();
  }, []);

  const onOkHandle = () => {
    if (form.users.length > 0) {
      postProjectTeamMembers(orgSid, teamName, form).then(() => {
        message.success(t('成员添加成功'));
        getTeamUsers();
        setInviteVisb(false);
      });
    } else {
      message.warning(t('成员为必选项'));
    }
  };

  const onAddMemberHandle = (role: number) => {
    setForm({
      ...form,
      role,
    });
    setInviteVisb(true);
  };

  const onRemoveMemberHandle = (role: number, userinfo: any) => {
    if (userinfo) {
      delProjectTeamMember(orgSid, teamName, role, userinfo.username).then(() => {
        message.success('已移除');
        getTeamUsers();
      });
    }
  };

  const onSelectUsersHandle = (value: any) => {
    setForm({
      ...form,
      users: value,
    });
  };

  return (
    <div>
      <PageHeader
        title='项目成员管理'
        description={<span>
          注：仅能添加团队内存在的成员，如需邀请成员，进入
          <Link to={getTeamMemberRouter(orgSid)}>团队成员管理</Link>页面邀请
        </span>}
      />
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
      <div className={s.content}>
        <MemberItem
          role={PERM_ENUM.ADMIN}
          list={members.admins}
          onAddMemberClick={onAddMemberHandle}
          onRemoveMemberClick={onRemoveMemberHandle}
        />
        <MemberItem
          role={PERM_ENUM.USER}
          list={members.users}
          onAddMemberClick={onAddMemberHandle}
          onRemoveMemberClick={onRemoveMemberHandle}
        />
      </div>
    </div>
  );
};

export default Group;
