import { generateOptions } from '@tencent/micro-frontend-shared/util';

export enum LibTypeEnum {
  PRIVATE = 'private',
  PUBLIC = 'public'
}

export const LIB_TYPE: any = {
  [LibTypeEnum.PRIVATE]: '私有依赖',
  [LibTypeEnum.PUBLIC]: '公共依赖',
};

enum LibEnvEnum {
  LINUX = 'linux',
  MAC = 'mac',
  WINDOWS = 'windows',
  ARM64_LINUX = 'linux_arm64'
}

export const LIB_ENV = {
  [LibEnvEnum.LINUX]: 'Linux',
  [LibEnvEnum.MAC]: 'Mac',
  [LibEnvEnum.WINDOWS]: 'Windows',
  [LibEnvEnum.ARM64_LINUX]: 'Linux ARM64',
};

export const LIB_ENV_OPTIONS = generateOptions(LIB_ENV, false);
