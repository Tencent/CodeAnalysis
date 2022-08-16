// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import React, { createContext, useReducer, useContext } from 'react';
import * as Constant from './constant';
import { noop } from 'lodash';

interface StateProps {
  userinfo: any; // 用户信息
}

interface ActionProps {
  type: string;
  payload: any;
}

const initialState: StateProps = {
  userinfo: {},
};

const StateContext = createContext<StateProps>(initialState);
const DispatchContext = createContext(noop);

const reducer = (state: StateProps, action: ActionProps) => {
  switch (action.type) {
    case Constant.SET_USERINFO: {
      const userinfo = action.payload;
      return {
        ...state,
        userinfo,
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
