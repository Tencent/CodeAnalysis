import { t } from '@tencent/micro-frontend-shared/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 用户等级 */
export enum LevelEnum {
  /** 普通用户 */
  NORMAL = 1,
  /** VIP 用户 */
  VIP,
  /** 超级VIP用户 */
  SUPER_VIP
}

/** 用户等级 kv */
export const LEVEL_CHOICES = {
  [LevelEnum.NORMAL]: t('普通用户'),
  [LevelEnum.VIP]: t('VIP用户'),
  [LevelEnum.SUPER_VIP]: t('超级VIP用户'),
};

/** 用户等级 options */
export const LEVEL_OPTIONS = generateOptions(LEVEL_CHOICES, true);

/** 用户状态  */
export enum StatusEnum {
  /** 已激活 */
  ACTIVE = 1,
  /** 待激活 */
  DISACTIVE,
  /** 已过期 */
  EXPIRED,
  /** 禁止 */
  FORBIDEN = 99,
}

/** 用户状态 kv */
export const STATUS_CHOICES = {
  [StatusEnum.ACTIVE]: t('已激活'),
  [StatusEnum.DISACTIVE]: t('待激活'),
  [StatusEnum.EXPIRED]: t('已过期'),
  [StatusEnum.FORBIDEN]: t('禁止'),
};

/** 用户状态 options */
export const STATUS_OPTIONS = [{
  label: STATUS_CHOICES[StatusEnum.ACTIVE],
  value: StatusEnum.ACTIVE,
}, {
  label: STATUS_CHOICES[StatusEnum.DISACTIVE],
  value: StatusEnum.DISACTIVE,
}];
