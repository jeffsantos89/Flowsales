 
import { createStore } from 'redux';

// Estado inicial
const initialState = {
  reports: [],
};

// Reducer
function reportingReducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_REPORTS':
      return { ...state, reports: action.payload };
    default:
      return state;
  }
}

// Store
const store = createStore(reportingReducer);

export default store;
