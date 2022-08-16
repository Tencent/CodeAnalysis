import React from 'react';

export interface StateProps {
  [name: string]: any;
}

export interface ActionProps {
  type: string;
  [name: string]: any
}

export type DispatchContextType<T> = React.Context<React.Dispatch<T>>;

export type Middleware<Action> = ({
  next,
  action,
  state,
}: {
  next: React.Dispatch<Action>;
  action: Action;
  state?: StateProps;
}) => void;

export type Reducer<State, Action> = (
  state: State,
  action: Action
) => State | undefined;

export interface Store<State, Action> {
  name: string;
  initialState: State;
  reducer: Reducer<State, Action>;
}

export interface ProviderProps<State, Action> {
  stores: Store<State, Action>[];
  middlewares?: Middleware<Action>[];
  children: JSX.Element[] | JSX.Element | React.ReactNode;
}
