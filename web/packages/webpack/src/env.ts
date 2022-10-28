export type Envs = {
  [key: string]: string | undefined
};

const envs: Envs = {
  PUBLIC_PATH: process.env.PUBLIC_PATH || '/',
  TITLE: process.env.TITLE,
  DESCRIPTION: process.env.DESCRIPTION,
  KEYWORDS: process.env.KEYWORDS,
  FAVICON: process.env.FAVICON,
  GIT_REVISION: process.env.GIT_REVISION || 'dirty',
};

// 用于生成index.runtime.html 可被替换的值
const runtimeKeys = ['TITLE', 'DESCRIPTION', 'KEYWORDS', 'FAVICON'];

const runtimeEnvs: Envs = {};

runtimeKeys.forEach((key) => {
  runtimeEnvs[key] = `__${key}__`;
});

export interface EnvConfig {
  envs: Envs,
  runtimeEnvs?: Envs
}

const envConfig: EnvConfig = {
  envs, runtimeEnvs,
};

export default envConfig;
