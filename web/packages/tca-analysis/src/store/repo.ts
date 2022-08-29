import { Store, Reducer } from '@tencent/micro-frontend-shared/hook-store/types';
import { DefaultAction } from './common';

/** 命名空间 */
export const NAMESPACE = 'REPO';

export const SET_CUR_REPO = 'SET_CUR_REPO';
export const SET_CUR_REPO_MEMBER = 'SET_CUR_REPO_MEMBER';

export interface RepoState {
  /** 代码库详情 */
  repoInfo: any;
  /** 代码库管理成员信息 */
  admins: any[];
  /** 代码库普通成员信息 */
  users: any[];
}

const initialState: RepoState = {
  repoInfo: {},
  admins: [],
  users: [],
};

const reducer: Reducer<RepoState, DefaultAction> = (state, action) => {
  switch (action.type) {
    case SET_CUR_REPO:
      return { ...state, repoInfo: action.payload };
    case SET_CUR_REPO_MEMBER: {
      const { admins = [], users = [] } = action.payload;
      return { ...state, admins, users };
    }
    default:
      return state;
  }
};

const store: Store<RepoState, DefaultAction> = {
  name: NAMESPACE,
  initialState,
  reducer,
};

export default store;

