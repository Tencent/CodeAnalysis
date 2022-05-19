import { t } from '@src/i18n/i18next';

export enum STATUSENUM {
  NORMAL,
  SUSPENSION,
  DOWN,
  EXPERIENCE
}

enum TYPEENUM {
  PUBLIC,
  PRIVATE
}

export const TOOL_STATUS = {
  [STATUSENUM.NORMAL]: '正常使用',
  [STATUSENUM.SUSPENSION]: '暂停使用',
  [STATUSENUM.DOWN]: '已下架',
  [STATUSENUM.EXPERIENCE]: '体验运营',
};

export const TOOL_TYPE = {
  [TYPEENUM.PUBLIC]: '公开',
  [TYPEENUM.PRIVATE]: '私有',
};

/**
 * 凭证类型
 */
export const AUTH_TYPE = {
  HTTP: 'password',
  SSH: 'ssh_token',
  OAUTH: 'oauth',
};

export const AUTH_TYPE_TXT = {
  HTTP: t('用户名 + 密码'),
  SSH: t('ssh'),
  OAUTH: t('OAuth'),
};

export const AUTH_DICT = {
  [AUTH_TYPE.HTTP]: AUTH_TYPE_TXT.HTTP,
  [AUTH_TYPE.SSH]: AUTH_TYPE_TXT.SSH,
  [AUTH_TYPE.OAUTH]: AUTH_TYPE_TXT.OAUTH,
};

/**
 * 仓库类型
 */
export const REPO_TYPE = {
  GIT: 'git',
  SVN: 'svn',
};

export const REPO_TYPE_OPTIONS = [REPO_TYPE.GIT, REPO_TYPE.SVN];

// 规则严重级别
export enum SEVERITYENUM {
  fatal = 1,
  error,
  warning,
  info
}

export const SEVERITY = {
  [SEVERITYENUM.fatal]: '致命',
  [SEVERITYENUM.error]: '错误',
  [SEVERITYENUM.warning]: '警告',
  [SEVERITYENUM.info]: '提示',
};


// 规则类别
export const CATEGORY = [
  {
    label: '功能',
    value: 1,
    name: 'correctness',
  },
  {
    label: '安全',
    value: 2,
    name: 'security',
  },
  {
    label: '性能',
    value: 3,
    name: 'performance',
  },
  {
    label: '可用性',
    value: 4,
    name: 'usability',
  },
  {
    label: '无障碍化',
    value: 5,
    name: 'accessibility',
  },
  {
    label: '国际化',
    value: 6,
    name: 'i18n',
  },
  {
    label: '代码风格',
    value: 7,
    name: 'convention',
  },
  {
    label: '其他',
    value: 8,
    name: 'other',
  },
];

export const SCM_PLATFORM = {
  1: '其他',
  2: '腾讯工蜂',
  3: 'CODING',
  4: 'GitHub',
  5: 'Gitee',
  6: 'GitLab',
};

export const AUTH_ID_PATH = {
  [AUTH_TYPE.HTTP]: 'scm_account',
  [AUTH_TYPE.SSH]: 'scm_ssh',
  [AUTH_TYPE.OAUTH]: 'scm_oauth',
}