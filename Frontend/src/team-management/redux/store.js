 
import { createStore } from 'redux';

// Estado inicial
const initialState = {
  teams: [],
};

// Reducer
function teamManagementReducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_TEAMS':
      return { ...state, teams: action.payload };
    default:
      return state;
  }
}

// Store
const store = createStore(teamManagementReducer);

export default store;
