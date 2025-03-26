// App.js
import React from 'react';
import { AppStoreWrapper } from './store/AppStoreWrapper'; // Importação do AppStoreWrapper
import MainNavigator from './navigation/MainNavigator'; // Exemplo de componente de navegação

const App = () => {
  return (
    <AppStoreWrapper>
      <MainNavigator />
    </AppStoreWrapper>
  );
};

export default App;