import { t } from '@src/utils/i18n';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';
import { NODE_ENABLED_OPTIONS, NODE_STATE_OPTIONS } from '@src/constant/node';

export const getNodeSearchFields = (tagOptions: any[]): SearchFormField[] => [{
  name: 'name',
  label: t('名称'),
  type: 'string',
  formType: 'input',
  placeholder: t('节点名称'),
}, {
  name: 'manager',
  label: t('负责人'),
  type: 'string',
  formType: 'input',
  placeholder: t('负责人'),
}, {
  name: 'state',
  label: t('状态'),
  type: 'string',
  formType: 'select',
  options: NODE_STATE_OPTIONS,
}, {
  name: 'enabled',
  label: t('可用性'),
  type: 'string',
  formType: 'select',
  options: NODE_ENABLED_OPTIONS,
}, {
  name: 'exec_tags',
  label: t('标签'),
  type: 'string',
  formType: 'select',
  placeholder: t('全部'),
  options: tagOptions,
}];
