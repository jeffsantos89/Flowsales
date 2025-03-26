// src/reducers/index.ts
import { combineReducers } from 'redux';
import someReducer from './someReducer'; // Importe seus reducers aqui

// Defina a estrutura do estado da aplicação
export interface RootState {
  some: ReturnType<typeof someReducer>;
  // Adicione outros estados aqui conforme necessário
}

// Combina todos os reducers
const rootReducer = combineReducers({
  some: someReducer,
  // Adicione outros reducers aqui
});

export default rootReducer; // Exporte o rootReducer
