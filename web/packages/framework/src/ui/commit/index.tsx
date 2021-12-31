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
