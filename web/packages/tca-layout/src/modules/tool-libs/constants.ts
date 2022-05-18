enum LibTypeEnum {
  PRIVATE = 'private',
  PUBLIC = 'public'
}

export const LIB_TYPE: any = {
  [LibTypeEnum.PRIVATE]: '私有依赖',
  [LibTypeEnum.PUBLIC]: '公共依赖'
}

enum LibEnvEnum {
  LINUX = 'linux',
  MAC = 'mac',
  WINDOWS = 'windows',
  ARM64_LINUX = 'arm64linux'
}

export const LIB_ENV = {
  [LibEnvEnum.LINUX]: 'linux',
  [LibEnvEnum.MAC]: 'mac',
  [LibEnvEnum.WINDOWS]: 'windows',
  [LibEnvEnum.ARM64_LINUX]: 'arm64linux'
}