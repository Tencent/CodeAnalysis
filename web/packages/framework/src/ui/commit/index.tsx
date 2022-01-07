// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import { render } from 'react-dom';
import { debug, getOrCreateBodyContainer } from '@src/utils';
import CommitUI, { CommitUIProps } from './ui';

const COMMIT_UI_CONTAINER = 'commit-ui';

export default (props: CommitUIProps) => {
  if (props.production && props.development) {
    debug('Rendering buffet ui');
    render(<CommitUI {...props} />, getOrCreateBodyContainer(COMMIT_UI_CONTAINER));
  }
};
