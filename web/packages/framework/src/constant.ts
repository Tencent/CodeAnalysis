// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

export default {
  LOG_LEVEL: 'LOG_LEVEL',
  MICRO_FRONTEND_API: 'MICRO_FRONTEND_API',
  MICRO_FRONTEND_API_LIST: 'MICRO_FRONTEND_API_LIST',
  MICRO_FRONTEND_SETTING_API: 'MICRO_FRONTEND_SETTING_API',
  MICRO_VERSION_INTERVAL: 'MICRO_VERSION_INTERVAL',
  MICRO_VERSION_ENABLED: 'MICRO_VERSION_ENABLED',
};

export const DEFAULT_MICRO_FRONTEND_API = '/static/configs.json';

export const DEFAULT_MICRO_FRONTEND_SETTING_API = '/static/settings.json';

export const DEFAULT_MICRO_VERSION_INTERVAL = 5 * 60 * 1000; // 5min
