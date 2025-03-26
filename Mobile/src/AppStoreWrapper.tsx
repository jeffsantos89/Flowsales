// src/store/AppStoreWrapper.tsx
import React from 'react';
import { Provider } from 'react-redux';
import { PersistGate } from 'redux-persist/integration/react';
import { Persistor } from 'redux-persist';
import { createStore } from 'redux';
import { persistStore } from 'redux-persist';
import { combineReducers } from 'redux';

// Add your reducers here
const rootReducer = combineReducers({
  // your reducers
});

export const store = createStore(rootReducer);
export const persistor = persistStore(store);

type AppStoreWrapperProps = {
  children: React.ReactNode;
};

export const AppStoreWrapper = ({ children }: AppStoreWrapperProps) => {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor as Persistor}>
        {children}
      </PersistGate>
    </Provider>
  );
};

export default rootReducer;


