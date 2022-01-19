// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import { info } from '@src/utils';
import './version-checking';

const GIT_REVISION = process.env.GIT_REVISION || '';

setTimeout(() => {
  info(`Framework 版本: ${GIT_REVISION || 'dirty'}`);
}, 0);
