// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

const initialState = {};

export interface ActionProps {
  type: string;
  payload: any;
}

const reducer = (state = initialState, action: ActionProps) => {
  switch (action.type) {
    default:
      return state;
  }
};
export default reducer;
