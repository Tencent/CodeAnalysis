import React, { createContext, useReducer, useContext } from 'react';
import { noop } from 'lodash';

interface ActionProps {
  type: string;
  payload: any;
}

const initialState = {};

const StateContext = createContext<{}>(initialState);
const DispatchContext = createContext(noop);

const reducer = (state: {}, action: ActionProps) => {
  switch (action.type) {
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
