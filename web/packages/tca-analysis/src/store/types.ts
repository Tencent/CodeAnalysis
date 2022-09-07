import { RepoState } from './repo';
import { TeamState } from './team';
import { DefaultAction } from './common';

export type State = TeamState | RepoState;
export type Action = DefaultAction;
