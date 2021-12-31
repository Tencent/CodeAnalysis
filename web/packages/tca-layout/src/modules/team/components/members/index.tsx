import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import copy2Clipboard from 'copy-to-clipboard';

import { Input, Button, Avatar, Modal, Row, Col, message, Tag } from 'coding-oa-uikit';
import PlusCircleIcon from 'coding-oa-uikit/lib/icon/PlusCircle';
import UserIcon from 'coding-oa-uikit/lib/icon/User';
import CloseCircleIcon from 'coding-oa-uikit/lib/icon/CloseCircle';

import { t } from '@src/i18n/i18next';
import { getTeamMember, getInviteCode, removeMember } from '@src/services/team';
import DangerModal from '@src/components/modal/danger-modal';
import { gUserImgUrl, getUserName } from '@src/utils';

import style from './style.scss';

const PERM_ENUM = {
  ADMIN: 1,
  USER: 2,
};

const PERM_CHOICES = {
  [PERM_ENUM.ADMIN]: {
    tit: t('管理员'),
    desc: t('（具备团队内全部权限，请谨慎赋予管理员权限）'),
  },
  [PERM_ENUM.USER]: {
    tit: t('普通成员'),
    desc: t('（具备团队内部分查看、创建项目等相关权限）'),
  },
};

interface IMemberItem {
  role: number;
  list: Array<any>;
  onAddMemberClick: (role: number) => void;
  onRemoveMemberClick: (role: number, userinfo: any) => void;
}

const MemberItem = ({ list, role, onAddMemberClick, onRemoveMemberClick }: IMemberItem) => (
  <div className={style.memberItem}>
    <div className={style.title}>
      {PERM_CHOICES[role].tit}
      <small className=" text-grey-7">{PERM_CHOICES[role].desc}</small>
    </div>
    <Row gutter={[16, 16]} align="middle" className={style.group}>
      <Col xl={6} lg={8} md={12} sm={24}>
        <Button
          type="link"
          icon={<PlusCircleIcon />}
          onClick={() => onAddMemberClick(role)}
        >
          {t('邀请成员')}
        </Button>
      </Col>
      {list.map((userinfo: any) => (
        <Col xl={6} lg={8} md={12} sm={24} key={userinfo.username}>
          <Avatar
            size="small"
            src={gUserImgUrl(userinfo.username)}
            alt={userinfo.nickname}
            icon={<UserIcon />}
          />
          <span className="ml-sm mr-xs">{userinfo.nickname}</span>
          <Button
            disabled={role === PERM_ENUM.ADMIN && list.length <= 1}
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

const Members = () => {
  const { orgSid }: any = useParams();
  const [members, setMembers] = useState<any>({
    admins: [],
    users: [],
  });
  const [inviteVisb, setInviteVisb] = useState(false);
  const [inviteUrl, setInviteUrl] = useState('');
  const [removeVisb, setRemoveVisb] = useState(false);
  const [removeUser, setRemoveUser] = useState<any>(null);

  useEffect(() => {
    if (orgSid) {
      getTeamMember(orgSid).then((response: any) => {
        setMembers(response);
      });
    }
  }, [orgSid]);

  const onAddMemberHandle = (role: number) => {
    getInviteCode(orgSid, { role }).then((response) => {
      const inviUrl = `${window.location.origin}/t/invite/${encodeURIComponent(response.invite_code)}`;
      setInviteUrl(inviUrl);
      setInviteVisb(true);
    });
  };

  const onRemoveMemberRequest = (role: number, userinfo: any) => {
    if (role === PERM_ENUM.ADMIN && members.admins && members.admins.length <= 1) {
      message.warning('团队不能没有任何管理员，禁止删除');
    } else if (userinfo) {
      removeMember(orgSid, role, userinfo.username).then(() => {
        message.success('移除成功');
        setRemoveVisb(false);
        setRemoveUser(null);
        getTeamMember(orgSid).then((response: any) => {
          setMembers(response);
        });
      });
    }
  };

  const onRemoveMemberHandle = (role: number, userinfo: any) => {
    setRemoveUser({ role, userinfo });
    setRemoveVisb(true);
  };

  const onCopyURLHandle = () => {
    message.success('已复制邀请链接');
    copy2Clipboard(inviteUrl);
    setInviteVisb(false);
  };

  return (
    <div className="pa-lg">
      <div className="mb-lg">
        <h3>{t('团队成员管理')}</h3>
      </div>
      <Modal
        title={t('邀请成员')}
        visible={inviteVisb}
        onOk={onCopyURLHandle}
        okText={t('复制链接')}
        onCancel={() => setInviteVisb(false)}
      >
        <Input disabled value={inviteUrl} />
        <div className="fs-12 pt-sm text-grey-6">
          * 分享链接，邀请成员，十分钟内有效
        </div>
      </Modal>
      <DangerModal
        title={t('移除用户')}
        visible={removeVisb}
        onCancel={() => {
          setRemoveVisb(false);
          setRemoveUser(null);
        }}
        onOk={() => {
          if (removeUser) {
            onRemoveMemberRequest(removeUser.role, removeUser.userinfo);
          }
        }}
        content={
          removeUser ? (
            <div>
              确定移除{' '}
              <Tag color="default">
                <b>
                  {PERM_CHOICES[removeUser?.role]?.tit}:{' '}
                  {getUserName(removeUser?.userinfo)}
                </b>
              </Tag>{' '}
              {t('？')}
            </div>
          ) : <></>
        }
      />
      <MemberItem
        list={members.admins}
        role={PERM_ENUM.ADMIN}
        onAddMemberClick={onAddMemberHandle}
        onRemoveMemberClick={onRemoveMemberHandle}
      />
      <MemberItem
        list={members.users}
        role={PERM_ENUM.USER}
        onAddMemberClick={onAddMemberHandle}
        onRemoveMemberClick={onRemoveMemberHandle}
      />
    </div>
  );
};

export default Members;
