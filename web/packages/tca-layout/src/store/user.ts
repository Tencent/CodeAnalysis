import { Store, Reducer } from '@tencent/micro-frontend-shared/hook-store/types';

/** 命名空间 */
export const NAMESPACE = 'USER';

export const SET_USERINFO = 'SET_USERINFO';
export const SET_PUPPYINFO = 'SET_PUPPYINFO';
export const SET_ORG_MANAGE_PERM = 'SET_ORG_MANAGE_PERM';

export interface UserState {
  userinfo: any;
  puppyInfo: any;
  hasOrgManagePerm: boolean;
}

export interface UserAction {
  type: string
  payload: any
}

const initialState: UserState = {
  userinfo: {},
  puppyInfo: {},
  hasOrgManagePerm: false,
};

const reducer: Reducer<UserState, UserAction> = (state, action) => {
  switch (action.type) {
    case SET_USERINFO:
      return { ...state, userinfo: action.payload };
    case SET_PUPPYINFO:
      return { ...state, puppyInfo: action.payload };
    case SET_ORG_MANAGE_PERM:
      return { ...state, hasOrgManagePerm: action.payload };
    default:
      return state;
  }
};

const store: Store<UserState, UserAction> = {
  name: NAMESPACE,
  initialState,
  reducer,
};

export default store;

