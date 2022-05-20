import { t } from '@src/i18n/i18next';

export const SCM_PLATFORM_ENUM = {
  TGIT: 1,
  TGITSAAS: 2,
  CODING: 3,
  GITHUB: 4,
  GITEE: 5,
  GITLAB: 6,
};

export const SCM_PLATFORM = {
  [SCM_PLATFORM_ENUM.TGIT]: t('工蜂内网'),
  [SCM_PLATFORM_ENUM.TGITSAAS]: t('腾讯工蜂'),
  [SCM_PLATFORM_ENUM.CODING]: t('Coding'),
  [SCM_PLATFORM_ENUM.GITHUB]: t('GitHub'),
  [SCM_PLATFORM_ENUM.GITEE]: t('Gitee'),
  [SCM_PLATFORM_ENUM.GITLAB]: t('GitLab'),
};

export const SCM_PLATFORM_OPTIONS = [{
  label: SCM_PLATFORM[SCM_PLATFORM_ENUM.TGITSAAS],
  value: SCM_PLATFORM_ENUM.TGITSAAS,
}, {
  label: SCM_PLATFORM[SCM_PLATFORM_ENUM.CODING],
  value: SCM_PLATFORM_ENUM.CODING,
}, {
  label: SCM_PLATFORM[SCM_PLATFORM_ENUM.GITHUB],
  value: SCM_PLATFORM_ENUM.GITHUB,
}, {
  label: SCM_PLATFORM[SCM_PLATFORM_ENUM.GITEE],
  value: SCM_PLATFORM_ENUM.GITEE,
}, {
  label: SCM_PLATFORM[SCM_PLATFORM_ENUM.GITLAB],
  value: SCM_PLATFORM_ENUM.GITLAB,
}];


export const DEFAULT_SCM_PLATFORM = [
  {
    scm_platform : 2,
    scm_platform_name : "tgitsaas",
    scm_platform_desc : '基于Git的企业级协作开发解决方案，腾讯研发关键系统',
  },
  {
    scm_platform : 4,
    scm_platform_name : "github",
    scm_platform_desc : '通过Git进行版本控制的软件源代码托管服务平台',
  },
  {
    scm_platform : 5,
    scm_platform_name : "gitee",  
    scm_platform_desc : '开源中国于2013年推出的基于Git的代码托管和协作开发平台',
  },
  {
    scm_platform : 6,
    scm_platform_name : "gitlab",
    scm_platform_desc : "由GitLab Inc.开发，一款基于Git的完全集成的软件开发平台",
  },
];