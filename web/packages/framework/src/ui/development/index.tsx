import React from 'react';
import ReactDom from 'react-dom';

import { getOrCreateBodyContainer } from '@src/utils';
import DevelopmentUI from './ui';

const DEV_UI_CONTAINER = 'development-ui';

ReactDom.render(<DevelopmentUI />, getOrCreateBodyContainer(DEV_UI_CONTAINER));
