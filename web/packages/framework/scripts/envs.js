// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const envs = {
  PUBLIC_PATH: process.env.PUBLIC_PATH || '/',
  MICRO_VERSION_INTERVAL: process.env.MICRO_VERSION_INTERVAL,
  MICRO_VERSION_ENABLED: process.env.MICRO_VERSION_ENABLED,
  MICRO_FRONTEND_SETTING_API: process.env.MICRO_FRONTEND_SETTING_API,
  TITLE: process.env.TITLE,
  DESCRIPTION: process.env.DESCRIPTION,
  KEYWORDS: process.env.KEYWORDS,
  FAVICON: process.env.FAVICON,
  MICRO_FRONTEND_API: process.env.MICRO_FRONTEND_API,
  GIT_REVISION: process.env.GIT_REVISION || 'dirty',
};

// 用于生成index.runtime.html 可被替换的值
const runtimeKeys = ['TITLE', 'DESCRIPTION', 'KEYWORDS', 'FAVICON', 'MICRO_FRONTEND_API', 'MICRO_FRONTEND_SETTING_API'];

const runtimeEnvs = {};

runtimeKeys.forEach((key) => {
  runtimeEnvs[key] = `__${key}__`;
});

module.exports = {
  envs,
  runtimeEnvs,
};
