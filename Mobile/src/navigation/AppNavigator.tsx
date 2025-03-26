import React, { Suspense } from 'react';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useSelector } from 'react-redux';
import { ActivityIndicator, View, StyleSheet, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { RootState } from '../store';

// Definição de tipos para as rotas
export type RootStackParamList = {
  Login: undefined;
  Products: undefined;
  Cart: undefined;
  Payment: {
    total: number;
    items: number;
  };
};

// Lazy loading com tratamento de erro
const screens = {
  LoginScreen: React.lazy(() =>
    import('../screens/LoginScreen').catch(() => ({
      default: () => <ErrorBoundary message="Erro ao carregar Login" />
    }))
  ),
  ProductsScreen: React.lazy(() =>
    import('../screens/ProductsScreen').catch(() => ({
      default: () => <ErrorBoundary message="Erro ao carregar Products" />
    }))
  ),
  CartScreen: React.lazy(() =>
    import('../screens/CartScreen').catch(() => ({
      default: () => <ErrorBoundary message="Erro ao carregar Cart" />
    }))
  ),
  PaymentScreen: React.lazy(() =>
    import('../screens/PaymentScreen').catch(() => ({
      default: () => <ErrorBoundary message="Erro ao carregar Payment" />
    }))
  ),
};

const Stack = createNativeStackNavigator<RootStackParamList>();

// Componente de loading com estilo separado
const LoadingScreen: React.FC = () => (
  <View style={styles.loadingContainer}>
    <ActivityIndicator size="large" color="#0000ff" />
  </View>
);

// Componente de erro
const ErrorBoundary: React.FC<{ message: string }> = ({ message }) => (
  <View style={styles.errorContainer}>
    <Text style={styles.errorText}>{message}</Text>
  </View>
);

// Componentes de navegação separados
const AuthenticatedStack: React.FC = () => (
  <>
    <Stack.Screen
      name="Products"
      component={screens.ProductsScreen}
      options={{
        headerShown: true,
        title: 'Produtos',
        headerTitleAlign: 'center',
      }}
    />
    <Stack.Screen
      name="Cart"
      component={screens.CartScreen}
      options={{
        headerShown: true,
        title: 'Carrinho',
        headerTitleAlign: 'center',
      }}
    />
    <Stack.Screen
      name="Payment"
      component={screens.PaymentScreen}
      options={{
        headerShown: true,
        title: 'Pagamento',
        headerTitleAlign: 'center',
      }}
    />
  </>
);

const UnAuthenticatedStack: React.FC = () => (
  <Stack.Screen
    name="Login"
    component={screens.LoginScreen}
    options={{
      headerShown: false,
    }}
  />
);

export const AppNavigator: React.FC = () => {
  const isAuthenticated = useSelector((state: RootState) => state.auth.isAuthenticated);

  return (
    <NavigationContainer>
      <Suspense fallback={<LoadingScreen />}>
        <Stack.Navigator
          screenOptions={{
            headerStyle: styles.header,
            headerTintColor: '#fff',
          }}
        >
          {isAuthenticated ? <AuthenticatedStack /> : <UnAuthenticatedStack />}
        </Stack.Navigator>
      </Suspense>
    </NavigationContainer>
  );
};

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  errorText: {
    color: 'red',
    fontSize: 16,
  },
  header: {
    backgroundColor: '#2196F3',
  },
});

export default AppNavigator;
