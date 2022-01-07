// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import Constant from './constant';

const initialState = {
  completed: false,
  projectCompleted: false,
};

export interface IAction {
  type: string;
  payload: any;
}

export default (state = initialState, action: IAction) => {
  switch (action.type) {
    case Constant.SET_LAYOUT_COMPLETED:
      return {
        ...state,
        completed: action.payload,
      };
    case Constant.SET_PROJECT_COMPLETED:
      return {
        ...state,
        projectCompleted: action.payload,
      };
    default:
      return state;
  }
};
