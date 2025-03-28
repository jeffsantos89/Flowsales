
import { createStore } from 'redux';

// Initial state
const initialState = {
  user: null,
  token: localStorage.getItem('auth_token')
};

// Reducer
function reducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_TOKEN':
      return { ...state, token: action.payload };
    default:
      return state;
  }
}

// Store
const store = createStore(reducer);

export default store;
