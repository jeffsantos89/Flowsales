import { configureStore, combineReducers } from '@reduxjs/toolkit';
import {
  persistStore,
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist';
import AsyncStorage from '@react-native-async-storage/async-storage';
import authReducer from './slices/authSlice';
import cartReducer from './slices/cartSlice';

// Combina os reducers
const rootReducer = combineReducers({
  auth: authReducer,
  cart: cartReducer,
});

// Configuração do Redux Persist
const persistConfig = {
  key: 'root',
  storage: AsyncStorage,
  whitelist: ['cart'], // Persiste apenas o slice 'cart'
};

// Cria o reducer persistido
const persistedReducer = persistReducer(persistConfig, rootReducer);

// Cria a store com o reducer persistido
export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

// Cria o persistor para a store
export const persistor = persistStore(store);

// Tipos para o RootState e AppDispatch
export type RootState = ReturnType<typeof rootReducer>;
export type AppDispatch = typeof store.dispatch;