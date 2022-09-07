import Constant from './constant';

const initialState = {
  completed: false,
  projectCompleted: false,
};

export interface IAction {
  type: string;
  payload: any;
}

const initReducer = (state = initialState, action: IAction) => {
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

export default initReducer;
