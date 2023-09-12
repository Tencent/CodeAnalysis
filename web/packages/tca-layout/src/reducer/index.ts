import initReducer from './initial';
import appReducer from './app';

const reducers = {
  APP: appReducer,
  INITIAL: initReducer,
};

export default reducers;
