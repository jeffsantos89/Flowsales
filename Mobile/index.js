// index.js
import { AppRegistry } from 'react-native';
import App from './App'; // Importação do componente App
import { name as appName } from './app.json'; // Nome do aplicativo

// Registra o componente raiz
AppRegistry.registerComponent(appName, () => App);