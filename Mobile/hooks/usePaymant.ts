import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigation, NavigationProp } from '@react-navigation/native';
// import { clearCart } from '../slices/cartSlice'; // Ensure the path is correct and the file exists

interface PaymentParams {
  cardNumber: string;
  cvv: string;
  expire: string;
  cartItems: { price: number; quantity: number }[];
  totalValue: number;
  setLoading: (loading: boolean) => void;
  dispatch: ReturnType<typeof useDispatch>;
  navigation: NavigationProp<any>;
}

const usePayment = ({
  cardNumber,
  cvv,
  expire,
  cartItems,
  totalValue,
  setLoading,
  dispatch,
  navigation,
}: PaymentParams) => {
  const handlePayment = async () => {
    try {
      setLoading(true);
      // Simula o processamento do pagamento
      await new Promise((resolve) => setTimeout(resolve, 2000));
      // Limpa o carrinho após o pagamento bem-sucedido
      dispatch(clearCart());
      // Navega para uma tela de sucesso
      navigation.navigate('Success');
    } catch (error) {
      console.error('Falha no pagamento', error);
    } finally {
      setLoading(false);
    }
  };

  return { handlePayment };
};

export { usePayment };

import { createSlice } from '@reduxjs/toolkit';

const cartSlice = createSlice({
  name: 'cart',
  initialState: [],
  reducers: {
    clearCart: (state) => {
      return [];
    },
  },
});

export const { clearCart } = cartSlice.actions;
export default cartSlice.reducer;