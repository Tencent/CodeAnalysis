import { BreadcrumbActions, GbcState, EMPTY_BREADCRUMB, UPDATE_BREADCRUMB_DATA } from './types';

const initialState: GbcState = {
  data: [],
};

export default function gbcReducer(state = initialState, action: BreadcrumbActions) {
  switch (action.type) {
    case UPDATE_BREADCRUMB_DATA: {
      return {
        data: action.payload.slice(),
      };
    }
    case EMPTY_BREADCRUMB:
      return {
        data: [],
      };
    default:
      return state;
  }
}
