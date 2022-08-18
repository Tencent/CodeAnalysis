/**
 * react hooks store
 * 来自 https://github.com/hangyangws/hooks-store
 */
import React, { Context, useMemo, createContext, Dispatch, useContext, useReducer } from 'react';

import { StateProps, ProviderProps, DispatchContextType } from './types';
import { getInitialState, getComdbinedReducer } from './utils';
import { applyMiddleware, genarateDefaultMiddlewares } from './middleware';

let StateContext: Context<StateProps>;
let DispatchContext: DispatchContextType<any>;

export const StoreProvider = <State, Action>(props: ProviderProps<State, Action>) => {
  const initialState: StateProps = useMemo(
    () => getInitialState(props.stores),
    [props.stores],
  );

  StateContext = useMemo(() => createContext<StateProps>(initialState), [initialState]);

  DispatchContext = useMemo(() => createContext<Dispatch<Action>>(() => 0), []);

  const combinedReducer = useMemo(() => getComdbinedReducer(props.stores), [props.stores]);

  const [state, dispatch] = useReducer(combinedReducer, initialState);

  // 让 dispatch 支持 middlewares
  const defaultMiddlewares = genarateDefaultMiddlewares<Action>();
  const middlewares = defaultMiddlewares.concat(props.middlewares ? props.middlewares : []);
  const enhancedDispatch = middlewares?.length
    ? applyMiddleware<Action>(state, dispatch, middlewares)
    : dispatch;

  return (
    <DispatchContext.Provider value={enhancedDispatch}>
      <StateContext.Provider value={state}>{props.children}</StateContext.Provider>
    </DispatchContext.Provider>
  );
};

export const useDispatchStore = <Action,>() => useContext(DispatchContext as DispatchContextType<Action>);

export const useStateStore = <State,>(nameSpace?: string) => {
  const store = useContext(StateContext);
  const state: State = nameSpace ? store[nameSpace] : store;
  return state;
};
