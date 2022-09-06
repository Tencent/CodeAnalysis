import { find } from 'lodash';
import Constant from './constant';


const initialState = {
  enterprise: {
    name: '腾讯云代码分析',
    key: 'tca',
    globalKey: 'tca',
    global_key: 'tca',
  },
  org: {},
  isOrgAdminUser: false,
  user: {},
  puppyInfo: {},
};

export interface IAction {
  type: string;
  payload: any;
}

const appReducer = (state = initialState, action: IAction) => {
  switch (action.type) {
    case Constant.SET_USERINFO:
      return {
        ...state,
        user: action.payload,
      };
    case Constant.SET_PUPPYINFO:
      return { ...state, puppyInfo: action.payload };
    case Constant.SET_ORG: {
      const isOrgAdminUser = !!find(action.payload?.admins || [], { username: state.user?.username });
      return {
        ...state,
        isOrgAdminUser,
        org: action.payload,
      };
    }
    default:
      return state;
  }
};

export default appReducer;
