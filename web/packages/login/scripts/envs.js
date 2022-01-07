// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const envs = {
  PUBLIC_PATH: process.env.PUBLIC_PATH || '/',
  TITLE: process.env.TITLE,
  DESCRIPTION: process.env.DESCRIPTION,
  KEYWORDS: process.env.KEYWORDS,
  FAVICON: process.env.FAVICON,
};

// 用于生成index.runtime.html 可被替换的值
const runtimeKeys = ['TITLE', 'DESCRIPTION', 'KEYWORDS', 'FAVICON'];

const runtimeEnvs = {};

runtimeKeys.forEach((key) => {
  runtimeEnvs[key] = `__${key}__`;
});

module.exports = {
  envs,
  runtimeEnvs,
};
