import { t } from '@src/utils/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

/** 任务执行状态 */
export enum ReportStateEnum {
  /** 运行中 */
  RUNNING = 1,
  /** 统计中 */
  CLOSEING = 2,
  /** 运行完成 */
  CLOSED = 3,
  /** 运行中止 */
  STOPPED = 4,
  /** 已过期 */
  EXPIRED = 5,
}

/** 任务执行状态 kv */
export const REPORT_STATE_CHOICES = {
  [ReportStateEnum.RUNNING]: t('运行中'),
  [ReportStateEnum.CLOSEING]: t('统计中'),
  [ReportStateEnum.CLOSED]: t('运行完成'),
  [ReportStateEnum.STOPPED]: t('运行中止'),
  [ReportStateEnum.EXPIRED]: t('已过期'),

};

/** 任务执行状态 options */
export const REPORT_STATE_OPTIONS = generateOptions(REPORT_STATE_CHOICES, true);
