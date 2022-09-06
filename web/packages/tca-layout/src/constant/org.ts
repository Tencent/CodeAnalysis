export enum OrgStatusEnum {
  ACTIVE = 1,
  DISACTIVE,
}

export const ORG_STATUS_CHOICES = {
  [OrgStatusEnum.ACTIVE]: '已激活',
  [OrgStatusEnum.DISACTIVE]: '审核中',
};

export enum OrgApplyStatusEnum {
  CHECKING = 1,
  CHECKED,
  CANCELED,
}

export const ORG_APPLY_STATUS_CHOICES = {
  [OrgApplyStatusEnum.CHECKING]: '审核中',
  [OrgApplyStatusEnum.CHECKED]: '审核完成',
  [OrgApplyStatusEnum.CANCELED]: '取消申请',
};

export enum OrgCheckResultEnum {
  PASS = 1,
  NO_PASS,
}

export const ORG_CHECK_RESULT_CHOICES = {
  [OrgCheckResultEnum.PASS]: '审核通过',
  [OrgCheckResultEnum.NO_PASS]: '审核不通过',
};

export enum OrgMemberRoleEnum {
  ADMIN = 1,
  USER,
}

export const ORG_MEMBER_ROLE_INFO = {
  [OrgMemberRoleEnum.ADMIN]: {
    tit: '管理员',
    desc: '（具备团队内全部权限，请谨慎赋予管理员权限）',
  },
  [OrgMemberRoleEnum.USER]: {
    tit: '普通成员',
    desc: '（具备团队内部分查看、创建项目等相关权限）',
  },
};
