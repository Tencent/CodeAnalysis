// Copyright (c) 2021-2022 THL A29 Limited
//
// This source code file is made available under MIT License
// See LICENSE for details
// ==============================================================================

import Constant from './constant';

const initialState = {
  enterprise: {
    name: '腾讯云代码分析',
    key: 'tca',
    globalKey: 'tca',
    global_key: 'tca',
  },
  org: {},
  user: null,
};

export interface IAction {
  type: string;
  payload: any;
}

export default (state = initialState, action: IAction) => {
  switch (action.type) {
    case Constant.SET_USERINFO:
      return {
        ...state,
        user: action.payload,
      };
    case Constant.SET_ORG:
      return {
        ...state,
        org: action.payload,
      };
    default:
      return state;
  }
};
