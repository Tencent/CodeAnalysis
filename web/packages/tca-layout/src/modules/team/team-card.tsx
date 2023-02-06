import React, { useMemo } from 'react';
import { Avatar, Badge, Tooltip } from 'coding-oa-uikit';
import { formatDateTime } from '@tencent/micro-frontend-shared/util';

// 项目内
import {
  OrgCheckResultEnum,
  ORG_CHECK_RESULT_CHOICES,
  OrgApplyStatusEnum,
  ORG_APPLY_STATUS_CHOICES,
  OrgStatusEnum,
} from '@src/constant';
import s from './style.scss';


const useBadeInfo = (status: number, check_remark: string) => {
  const info = useMemo(() => {
    if (status === OrgApplyStatusEnum.CHECKING) {
      return {
        color: '#06f',
        text: ORG_APPLY_STATUS_CHOICES[OrgApplyStatusEnum.CHECKING],
        remark: '平台会在1-2个工作日内完成审核，请稍候',
      };
    }
    if (status === OrgApplyStatusEnum.CANCELED) {
      return {
        color: '#eb333f',
        text: ORG_APPLY_STATUS_CHOICES[OrgApplyStatusEnum.CANCELED],
        remark: check_remark,
      };
    }
    return {
      color: '#eb333f',
      text: ORG_CHECK_RESULT_CHOICES[OrgCheckResultEnum.NO_PASS],
      remark: check_remark,
    };
  }, [status, check_remark]);
  return info;
};

interface TeamCardProps {
  data: any;
}

const TeamCard = ({ data }: TeamCardProps) => {
  const { name, status, created_time: createdTime, last_perm_apply: lastPermApply } = data;
  const { text, color, remark } = useBadeInfo(lastPermApply?.status, lastPermApply?.check_remark ?? '团队信息审核失败');

  const children = <div className={s.item}>
    <Avatar size="large" style={{ backgroundColor: '#adbacc' }}>
      {(name[0] as string).toUpperCase()}
    </Avatar>
    <div className={s.content}>
      <h3>{name}</h3>
      <p className={s.time}>创建于：{formatDateTime(createdTime)}</p>
    </div>
  </div>;

  if (status > OrgStatusEnum.ACTIVE) {
    return <Badge.Ribbon
      color={color}
      text={text}
    >
      <Tooltip title={<span style={{ color: '#fff' }}>{remark}</span>} color={color} >
        {children}
      </Tooltip>
    </Badge.Ribbon>;
  }

  return children;
};

export default TeamCard;
