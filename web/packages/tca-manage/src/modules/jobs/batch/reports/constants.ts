import { t } from '@src/utils/i18n';
import { flatMap } from 'lodash';
import { generateOptions } from '@tencent/micro-frontend-shared/util';
import { SearchFormField  } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { FilterField } from '@tencent/micro-frontend-shared/util/types';
import { STATE_OPTIONS, RESULT_OPTIONS } from '@src/modules/jobs/constants';

/** 任务执行状态 */
export enum BatchStateEnum {
  /** 运行中 */
  RUNNING = 1,
  /** 运行完成 */
  CLOSED = 3,
  /** 已过期 */
  EXPIRED = 5,
}

/** 任务执行状态 kv */
export const BATCH_STATE_CHOICES = {
  [BatchStateEnum.RUNNING]: t('运行中'),
  [BatchStateEnum.CLOSED]: t('运行完成'),
  [BatchStateEnum.EXPIRED]: t('已过期'),
};

/** 任务执行状态 options */
export const BATCH_STATE_OPTIONS = generateOptions(BATCH_STATE_CHOICES, true);

/** 定义筛选字段结构 */
export const JOB_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'state',
  label: '状态',
  type: 'number',
  formType: 'select',
  options: STATE_OPTIONS,
}, {
  name: 'result_code_gte',
  label: '结果码',
  placeholder: '结果码 >=',
  type: 'number',
  formType: 'input',
}, {
  name: 'result_code_lte',
  placeholder: '结果码 <=',
  type: 'number',
  formType: 'input',
}];

/** 高级搜索的筛选字段 */
export const JOB_MORE_SEARCH_FIELDS: SearchFormField[] = [{
  name: 'result_msg',
  label: t('详情'),
  type: 'string',
  formType: 'input',
  placeholder: t('结果详情'),
}, {
  name: 'result',
  label: '结果',
  type: 'number',
  formType: 'select',
  options: RESULT_OPTIONS,
}, {
  name: 'repo_id',
  label: t('代码库 ID'),
  type: 'number',
  formType: 'input',
}, {
  name: 'project_id',
  label: t('项目 ID'),
  type: 'number',
  formType: 'input',
}, {
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
}];

/** 整体的筛选字段 */
export const ORI_JOB_FILTER_FIELDS = JOB_SEARCH_FIELDS.concat(JOB_MORE_SEARCH_FIELDS);

/** 分析记录整体的筛选字段 */
export const JOB_FILTER_FIELDS: FilterField[] = flatMap(ORI_JOB_FILTER_FIELDS, (filter: any) => {
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
