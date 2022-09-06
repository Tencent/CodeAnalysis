import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import copy2Clipboard from 'copy-to-clipboard';
import { get } from 'lodash';
import { Input, Button, Modal, Row, Col, message, Tag } from 'coding-oa-uikit';
import PlusCircleIcon from 'coding-oa-uikit/lib/icon/PlusCircle';
import CloseCircleIcon from 'coding-oa-uikit/lib/icon/CloseCircle';
import { DangerModal } from '@tencent/micro-frontend-shared/component/modal';
import UserAvatar from '@tencent/micro-frontend-shared/component/user-avatar';

import { OrgMemberRoleEnum, ORG_MEMBER_ROLE_INFO } from '@src/constant';
import { getTeamMember, getInviteCode, removeMember } from '@src/services/team';
import { getNickName, getUserAvatarURL } from '@src/utils';
import style from './style.scss';

interface MemberItemProps {
  role: number;
  list: Array<any>;
  onAddMemberClick: (role: number) => void;
  onRemoveMemberClick: (role: number, userinfo: any) => void;
}

const MemberItem = ({ list, role, onAddMemberClick, onRemoveMemberClick }: MemberItemProps) => {
  const { t } = useTranslation();
  const { tit, desc }: any = get(ORG_MEMBER_ROLE_INFO, role, {});
  return (
    <div className={style.memberItem}>
      <div className={style.title}>
        {tit}
        <small className=" text-grey-7">{desc}</small>
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
        {list.map((userinfo: any) => {
          const { avatar, avatar_url: avatarUrl } = userinfo;
          const url = avatar || avatarUrl || getUserAvatarURL(userinfo);
          return (
            <Col xl={6} lg={8} md={12} sm={24} key={userinfo.username}>
              <UserAvatar size="small" url={url} nickname={getNickName(userinfo)} />
              <Button
                disabled={role === OrgMemberRoleEnum.ADMIN && list.length <= 1}
                type="text"
                icon={<CloseCircleIcon />}
                size="small"
                onClick={() => onRemoveMemberClick(role, userinfo)}
              />
            </Col>
          );
        })}
      </Row>
    </div>
  );
};

const Members = () => {
  const [members, setMembers] = useState<any>({
    admins: [],
    users: [],
  });
  const [inviteVisb, setInviteVisb] = useState(false);
  const [inviteUrl, setInviteUrl] = useState('');
  const [removeVisb, setRemoveVisb] = useState(false);
  const [removeUser, setRemoveUser] = useState<any>(null);

  const { orgSid }: any = useParams();
  const { t } = useTranslation();

  useEffect(() => {
    if (orgSid) {
      getTeamMember(orgSid).then((response: any) => {
        setMembers(response);
      });
    }
  }, [orgSid]);

  /** 邀请成员，生成邀请链接 */
  const onAddMemberHandle = (role: number) => {
    getInviteCode(orgSid, { role }).then(({ invite_code: inviteCode }) => {
      const inviUrl = `${window.location.origin}/t/invite/${encodeURIComponent(inviteCode)}`;
      setInviteUrl(inviUrl);
      setInviteVisb(true);
    });
  };

  /** 移除成员 */
  const onRemoveMemberRequest = (role: number, userinfo: any) => {
    if (role === OrgMemberRoleEnum.ADMIN && members.admins.length <= 1) {
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
                  {get(ORG_MEMBER_ROLE_INFO, `${removeUser.role}.tit`, ' ')}
                  {getNickName(removeUser.userinfo)}
                </b>
              </Tag>{' '}
              {t('？')}
            </div>
          ) : <></>
        }
      />
      <MemberItem
        list={members.admins}
        role={OrgMemberRoleEnum.ADMIN}
        onAddMemberClick={onAddMemberHandle}
        onRemoveMemberClick={onRemoveMemberHandle}
      />
      <MemberItem
        list={members.users}
        role={OrgMemberRoleEnum.USER}
        onAddMemberClick={onAddMemberHandle}
        onRemoveMemberClick={onRemoveMemberHandle}
      />
    </div>
  );
};

export default Members;
