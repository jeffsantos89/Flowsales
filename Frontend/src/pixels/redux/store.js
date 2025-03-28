 
import { createStore } from 'redux';

// Estado inicial
const initialState = {
  pixels: [],
};

// Reducer
function pixelReducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_PIXELS':
      return { ...state, pixels: action.payload };
    default:
      return state;
  }
}

// Store
const store = createStore(pixelReducer);

export default store;
