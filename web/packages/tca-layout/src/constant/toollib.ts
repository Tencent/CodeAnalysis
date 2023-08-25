import { generateOptions } from '@tencent/micro-frontend-shared/util';
import { UserData } from './user';

/** 依赖类型 enum */
export enum LibTypeEnum {
  PRIVATE = 'private',
  PUBLIC = 'public'
}

/** 依赖 kv */
export const LIB_TYPE_CHOICES = {
  [LibTypeEnum.PRIVATE]: '私有依赖',
  [LibTypeEnum.PUBLIC]: '公共依赖',
};

/** 依赖环境 enum */
export enum LibEnvEnum {
  LINUX = 'linux',
  MAC = 'mac',
  WINDOWS = 'windows',
  ARM64_LINUX = 'linux_arm64'
}

/** 依赖环境 kv */
export const LIB_ENV_CHOICES = {
  [LibEnvEnum.LINUX]: 'Linux',
  [LibEnvEnum.MAC]: 'Mac',
  [LibEnvEnum.WINDOWS]: 'Windows',
  [LibEnvEnum.ARM64_LINUX]: 'Linux ARM64',
};

/** 依赖环境options  */
export const LIB_ENV_OPTIONS = generateOptions(LIB_ENV_CHOICES);

/** 依赖数据结构 */
export interface LibData {
  /** ID */
  id: number;
  /** 依赖名称 */
  name: string;
  /** 依赖描述 */
  description?: string;
  /** 依赖类型 */
  lib_type: LibTypeEnum;
  /** 依赖环境 */
  os: LibEnvEnum[],
  /** 环境变量 */
  envs: {
    [key: string]: string
  },
  /** 创建时间 */
  created_time: string;
  /** 更新时间 */
  modified_time: string;
  /** 负责人 */
  creator: string | UserData
}
