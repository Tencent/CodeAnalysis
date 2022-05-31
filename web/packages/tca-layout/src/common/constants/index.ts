// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

// 分页默认值
export const DEFAULT_PAGER = {
  count: 0,
  pageSize: 10,
  pageStart: 0,
};

export const BASE_ROUTE_PREFIX = '/code-analysis/repos/:repoId?';

export const PROJECT_ROUTE_PREFIX = `${BASE_ROUTE_PREFIX}/projects/:projectId`;
