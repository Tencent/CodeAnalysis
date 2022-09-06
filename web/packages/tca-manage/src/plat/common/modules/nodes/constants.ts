import { t } from '@tencent/micro-frontend-shared/i18n';
import { SearchFormField } from '@tencent/micro-frontend-shared/tdesign-component/search';

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
  name: 'exec_tags',
  label: t('标签'),
  type: 'string',
  formType: 'select',
  placeholder: t('全部'),
  options: tagOptions,
}];
