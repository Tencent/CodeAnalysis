// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React from 'react';
import ReactDom from 'react-dom';

import { getOrCreateBodyContainer } from '@src/utils';
import DevelopmentUI from './ui';

const DEV_UI_CONTAINER = 'development-ui';

ReactDom.render(<DevelopmentUI />, getOrCreateBodyContainer(DEV_UI_CONTAINER));
