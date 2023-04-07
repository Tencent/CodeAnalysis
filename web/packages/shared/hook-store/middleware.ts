import React, { useCallback, useRef } from 'react';

import { StateProps, Middleware } from './types';

export const useApplyMiddleware = <Action>(
  state: StateProps,
  dispatch: React.Dispatch<Action>,
  middlewares: Middleware<Action>[],
) => {
  const stateRef = useRef<any>(null);
  stateRef.current = state;
  // in the same middleware three should be the shame next function
  // so there must cache the index of current
  const executeMiddleware = useCallback((index: number) => (action: Action) => {
    if (index >= middlewares.length) {
      dispatch(action);
      return;
    }
    middlewares[index]({ next: executeMiddleware(index + 1), action, state: stateRef.current });
  }, [dispatch, middlewares]);

  return useCallback((action: Action) => {
    if (middlewares?.length) {
      middlewares[0]({ next: executeMiddleware(1), action, state: stateRef.current });
    } else {
      dispatch(action);
    }
  }, [dispatch, middlewares, executeMiddleware]);
};

/** 生成默认的配置的中间件 */
export const genarateDefaultMiddlewares = <Action>() => {
  const actionLog: Middleware<Action> = ({ next, action, state }) => {
    const log = {
      state,
      action,
    };

    console.table(log);

    next(action);
  };
  if (process.env.NODE_ENV === 'development') {
    return [actionLog];
  }
  return [];
};
