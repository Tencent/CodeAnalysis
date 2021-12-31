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
