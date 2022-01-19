// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import { useLocation } from 'react-router-dom';

/**
 * 获取当前页面查询参数 hooks
 */
export const useQuery = () => new URLSearchParams(useLocation().search);
