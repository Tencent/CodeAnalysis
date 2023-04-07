import { t } from '@src/utils/i18n';
import { generateOptions } from '@tencent/micro-frontend-shared/util';

import { OAuthSettingData } from '@src/modules/oauth/types';

/** OAuth平台类型 */
export enum ScmPlatformEnum {
  /** 腾讯工蜂 */
  TGIT = 1,
  /** 腾讯工蜂外网 */
  TGITSAAS,
  /** Coding */
  CODING,
  GITHUB,
  GITEE,
  GITLAB,
}

/** OAuth平台类型名称 */
export enum ScmPlatformNameEnum {
  TGIT = 'tgit',
  TGITSAAS = 'tgitsaas',
  CODING = 'coding',
  GITHUB = 'github',
  GITEE = 'gitee',
  GITLAB = 'gitlab',
}

/** OAuth平台类型 kv */
export const SCM_PLATFORM_CHOICES = {
  [ScmPlatformEnum.TGIT]: t('腾讯工蜂(OA)'),
  [ScmPlatformEnum.TGITSAAS]: t('腾讯工蜂'),
  [ScmPlatformEnum.CODING]: t('Coding'),
  [ScmPlatformEnum.GITHUB]: t('GitHub'),
  [ScmPlatformEnum.GITEE]: t('Gitee'),
  [ScmPlatformEnum.GITLAB]: t('GitLab'),
};

/** OAuh 平台类型 URL前缀 */
export const SCM_PLATFORM_URL_PREFIX_CHOICES = {
  [ScmPlatformEnum.TGITSAAS]: 'https://git.code.tencent.com/',
  [ScmPlatformEnum.GITHUB]: 'https://github.com/',
  [ScmPlatformEnum.GITEE]: 'https://gitee.com/',
  [ScmPlatformEnum.GITLAB]: 'https://gitlab.com/',
};

/** OAuth 平台类型 options */
export const SCM_PLATFORM_OPTIONS = generateOptions(SCM_PLATFORM_CHOICES, true);

/** OAuth 平台类型详细配置 */
export const DEFAULT_SCM_PLATFORM: OAuthSettingData[] = [
  {
    scm_platform: ScmPlatformEnum.TGITSAAS,
    scm_platform_name: ScmPlatformNameEnum.TGITSAAS,
    scm_platform_desc: '基于Git的企业级协作开发解决方案，腾讯研发关键系统',
  },
  {
    scm_platform: ScmPlatformEnum.GITHUB,
    scm_platform_name: ScmPlatformNameEnum.GITHUB,
    scm_platform_desc: '通过Git进行版本控制的软件源代码托管服务平台',
  },
  {
    scm_platform: ScmPlatformEnum.GITEE,
    scm_platform_name: ScmPlatformNameEnum.GITEE,
    scm_platform_desc: '开源中国于2013年推出的基于Git的代码托管和协作开发平台',
  },
  {
    scm_platform: ScmPlatformEnum.GITLAB,
    scm_platform_name: ScmPlatformNameEnum.GITLAB,
    scm_platform_desc: '由GitLab Inc.开发的基于Git的完全集成的软件开发平台',
  },
];

