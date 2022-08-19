import React from 'react';

import { StateProps, Middleware } from './types';

export const applyMiddleware = <Action>(
  state: StateProps,
  dispatch: React.Dispatch<Action>,
  middlewares: Middleware<Action>[],
) => {
  // in the same middleware three should be the shame next function
  // so there must cache the index of current
  const executeMiddleware = (index: number) => (action: Action) => {
    if (index >= middlewares.length) {
      dispatch(action);
      return;
    }

    middlewares[index]({ next: executeMiddleware(index + 1), action, state });
  };

  return (action: Action) => {
    middlewares[0]({ next: executeMiddleware(1), action, state });
  };
};

/** 生成默认的配置的中间件 */
export const genarateDefaultMiddlewares = <Action>() => {
  const actionLog: Middleware<Action> = ({ next, action, state }) => {
    const log = {
      action,
      state,
    };

    console.table(log);

    next(action);
  };
  if (process.env.NODE_ENV === 'development') {
    return [actionLog];
  }
  return [];
};
