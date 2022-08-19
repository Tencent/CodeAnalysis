import moment from 'moment';
import { flatMap } from 'lodash';

import { t } from '@tencent/micro-frontend-shared/i18n';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { FilterField } from '@tencent/micro-frontend-shared/util/types';
import { generateOptions, formatDate } from '@tencent/micro-frontend-shared/util';

/** 任务执行状态 */
export enum StateEnum {
  /** 等待中 */
  WAITING,
  /** 执行中 */
  RUNNING,
  /** 已结束 */
  CLOSED,
  /** 入库中 */
  CLOSING,
  /** 初始化中 */
  INITING,
  /** 已初始化 */
  INITED,
}

/** 任务执行状态 kv */
export const STATE_CHOICES = {
  [StateEnum.WAITING]: t('等待中'),
  [StateEnum.RUNNING]: t('执行中'),
  [StateEnum.CLOSED]: t('已结束'),
  [StateEnum.CLOSING]: t('入库中'),
  [StateEnum.INITING]: t('初始化'),
  [StateEnum.INITED]: t('已初始化'),
};

/** 任务执行状态 options */
export const STATE_OPTIONS = generateOptions(STATE_CHOICES, true);

/** 任务执行结果 */
export enum ResultEnum {
  /** 执行成功 */
  SUCCESS,
  /** 执行异常 */
  EXCEPTION
}

/** 任务执行结果 kv */
export const RESULT_CHOICES = {
  [ResultEnum.SUCCESS]: t('执行成功'),
  [ResultEnum.EXCEPTION]: t('执行异常'),
};

/** 任务执行结果 options */
export const RESULT_OPTIONS = generateOptions(RESULT_CHOICES, true);

/** 定义筛选字段结构 */
export const JOB_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'state',
  label: '状态',
  type: 'number',
  formType: 'select',
  options: STATE_OPTIONS,
}, {
  name: 'result',
  label: '结果',
  type: 'number',
  formType: 'select',
  options: RESULT_OPTIONS,
}, {
  name: 'repo',
  label: 'ID',
  type: 'string',
  formType: 'input',
  placeholder: '代码库 ID',
}];

/** 高级搜索的筛选字段 */
export const JOB_MORE_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'result_msg',
  label: t('详情'),
  type: 'string',
  formType: 'input',
  placeholder: t('结果详情'),
}, {
  name: 'created_from',
  label: t('渠道'),
  type: 'string',
  formType: 'input',
  placeholder: t('启动渠道'),
}, {
  name: 'scm_url',
  label: t('URL'),
  type: 'string',
  formType: 'input',
  placeholder: t('代码库地址'),
}, {
  name: 'creator',
  label: t('启动人'),
  type: 'string',
  formType: 'input',
  placeholder: t('启动人'),
}];

/** 整体的筛选字段 */
export const JOB_FILTER_FIELDS = JOB_SEARCH_FIELDS.concat(JOB_MORE_SEARCH_FIELDS);

/** 归档任务日期类型 */
export enum PeriodEnum {
  MONTH = 'month',
  DAY = 'day'
}

/** 归档任务日期类型 kv */
export const PERIOD_CHOICES = {
  [PeriodEnum.MONTH]: t('当月'),
  [PeriodEnum.DAY]: t('当日'),
};

/** 归档日期类型 options */
export const PERIOD_OPTIONS = generateOptions(PERIOD_CHOICES);

/** 归档分析记录默认筛选项 */
export const DEFAULT_ARCHIVE_JOB_FILTER = {
  period: 'month',
  date: formatDate(moment()),
};

/** 归档分析记录基础筛选项 */
export const ARCHIVE_JOB_SEARCH_FIELDS: SearchFormField[] = [{
  label: '范围',
  name: 'date',
  type: 'time',
  formType: 'datepicker',
  defaultValue: DEFAULT_ARCHIVE_JOB_FILTER.date,
}, {
  name: 'period',
  type: 'string',
  formType: 'select',
  options: PERIOD_OPTIONS,
  defaultValue: DEFAULT_ARCHIVE_JOB_FILTER.period,
}, {
  name: 'result',
  label: '结果',
  type: 'number',
  formType: 'select',
  options: RESULT_OPTIONS,
}];

/** 归档分析记录高级筛选项 */
export const ARCHIVE_JOB_MORE_SEARCH_FIELDS: SearchFormField[] = [
  ...JOB_MORE_SEARCH_FIELDS,
  {
    name: 'create_time',
    label: '开始',
    type: 'string',
    formType: 'rangepicker',
    placeholder: '任务开始日期',
  }, {
    name: 'end_time',
    label: '结束',
    type: 'string',
    formType: 'rangepicker',
    placeholder: '任务结束日期',
  },
];

/** 归档分析记录整体的筛选字段 */
const ARCHIVE_JOB_ALL_SEARCH_FIELDS = ARCHIVE_JOB_SEARCH_FIELDS.concat(ARCHIVE_JOB_MORE_SEARCH_FIELDS);

export const ARCHIVE_JOB_FILTER_FIELDS: FilterField[] = flatMap(ARCHIVE_JOB_ALL_SEARCH_FIELDS, (filter: any) => {
  if (filter.formType === 'rangepicker') {
    return [{
      name: `${filter.name}_gte`,
      type: filter.type,
    }, {
      name: `${filter.name}_lte`,
      type: filter.type,
    }];
  }
  return {
    name: filter.name,
    type: filter.type,
  };
});
