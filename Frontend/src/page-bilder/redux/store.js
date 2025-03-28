
import { createStore } from 'redux';

// Estado inicial
const initialState = {
  pages: [],
  templates: [],
};

// Reducer
function pageBuilderReducer(state = initialState, action) {
  switch (action.type) {
    case 'SET_PAGES':
      return { ...state, pages: action.payload };
    case 'SET_TEMPLATES':
      return { ...state, templates: action.payload };
    default:
      return state;
  }
}

// Store
const store = createStore(pageBuilderReducer);

export default store;
