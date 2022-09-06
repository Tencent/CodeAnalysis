import { Store, Reducer } from '@tencent/micro-frontend-shared/hook-store/types';
import { DefaultAction } from './common';

/** 命名空间 */
export const NAMESPACE = 'TEAM';

export const SET_PROJECT_MEMBER = 'SET_PROJECT_MEMBER';
export const SET_REPOS = 'SET_REPOS';
export const SET_REPOS_LOADING = 'SET_REPOS_LOADING';

export interface TeamState {
  /** 项目组代码库列表 */
  repos: any[];
  /** 代码库列表加载状态 */
  reposLoading: boolean;
  /** 项目组管理员成员信息 */
  admins: any[];
  /** 项目组普通员成员信息 */
  users: any[]
}

const initialState: TeamState = {
  repos: [],
  reposLoading: false,
  admins: [],
  users: [],
};

const reducer: Reducer<TeamState, DefaultAction> = (state, action) => {
  switch (action.type) {
    case SET_PROJECT_MEMBER: {
      const { admins = [], users = [] } = action.payload;
      return { ...state, admins, users };
    }
    case SET_REPOS:
      return { ...state, repos: action.payload };
    case SET_REPOS_LOADING:
      return { ...state, reposLoading: action.payload };
    default:
      return state;
  }
};

const store: Store<TeamState, DefaultAction> = {
  name: NAMESPACE,
  initialState,
  reducer,
};

export default store;

