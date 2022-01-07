// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import MicroApplication from '@src/meta/application';

/**
 * 微前端数据加载器
 */
export interface MicroApplicationLoader {
  readonly enabled: () => Promise<boolean>;
  readonly loadMeta: (production?: MicroApplication[]) => Promise<MicroApplication[]>;
  readonly renderUI: (production: MicroApplication[], development: MicroApplication[]) => any;
  readonly exit: (reload: boolean) => any;
}
