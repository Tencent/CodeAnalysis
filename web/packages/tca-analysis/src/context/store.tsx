// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { createContext, useReducer, useContext } from 'react';
import { noop } from 'lodash';

import {
  SET_REPOS,
  SET_CUR_REPO,
  SET_CUR_REPO_MEMBER,
  SET_PROJECT_MEMBER,
  SET_REPOS_LOADING,
} from './constant';

interface MemberIProps {
  admins: Array<any>;
  users: Array<any>;
}

interface StateProps {
  repos: any; // 所有代码库列表
  reposLoading: boolean; // 代码库请求状态
  curRepo: any; // 当前代码库信息
  curRepoMember: any; // 当前代码库的成员信息
  projectMembers: MemberIProps;
}

interface ActionProps {
  type: string;
  payload: any;
}

const initialState: StateProps = {
  repos: [],
  reposLoading: false,
  curRepo: {},
  projectMembers: {
    admins: [],
    users: [],
  },
  curRepoMember: {
    admins: [],
    users: [],
  },
};

const StateContext = createContext<StateProps>(initialState);
const DispatchContext = createContext(noop);

const reducer = (state: StateProps, action: ActionProps) => {
  switch (action.type) {
    case SET_REPOS: {
      return {
        ...state,
        repos: action.payload,
      };
    }
    case SET_REPOS_LOADING: {
      return {
        ...state,
        reposLoading: action.payload,
      };
    }
    case SET_CUR_REPO: {
      return {
        ...state,
        curRepo: action.payload,
      };
    }
    case SET_CUR_REPO_MEMBER: {
      return {
        ...state,
        curRepoMember: action.payload,
      };
    }
    case SET_PROJECT_MEMBER: {
      return {
        ...state,
        projectMembers: action.payload,
      };
    }
    default: {
      return state;
    }
  }
};

const StoreProvider = ({ children }: { children: any }) => {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <StateContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>{children}</DispatchContext.Provider>
    </StateContext.Provider>
  );
};

const useStateStore = () => useContext(StateContext);
const useDispatchStore = () => useContext(DispatchContext);

export { StoreProvider, useStateStore, useDispatchStore };
