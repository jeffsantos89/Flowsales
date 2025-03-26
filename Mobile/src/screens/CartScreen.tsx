import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import React from 'react';
import { View, Text, FlatList, Button, StyleSheet } from 'react-native';
import { useSelector, useDispatch } from 'react-redux';
import { RootState, AppDispatch } from '../store';

interface CartItem {
  productId: number;
  name: string;
  price: number;
  quantity: number;
}

interface CartState {
  items: CartItem[];
}

const initialState: CartState = {
  items: [] as CartItem[]
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    removeItem: (state, action: PayloadAction<number>) => {
      state.items = state.items.filter(item => item.productId !== action.payload);
    },
    clearItems: (state) => {
      state.items = [];
    },
    addItem: (state, action: PayloadAction<CartItem>) => {
      const existingItem = state.items.find(item => item.productId === action.payload.productId);
      if (existingItem) {
        existingItem.quantity += 1;
      } else {
        state.items.push({ ...action.payload, quantity: 1 });
      }
    }
  }
});

export const { removeItem: removeFromCart, clearItems: clearCart, addItem: addToCart } = cartSlice.actions;
export const cartReducer = cartSlice.reducer;

const CartScreen: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const cartItems = useSelector((state: RootState) => state.cart.items) as unknown as CartItem[];

  const handleRemoveItem = (productId: number) => {
    dispatch(removeFromCart(productId));
  };

  const handleClearCart = () => {
    dispatch(clearCart());
  };

  return (
    <View style={styles.container}>
      <FlatList<CartItem>
        data={cartItems}
        keyExtractor={(item) => item.productId.toString()}
        renderItem={({ item }) => (
          <View style={styles.item}>
            <Text>{item.name}</Text>
            <Text>{item.price}</Text>
            <Text>{item.quantity}</Text>
            <Button title="Remove" onPress={() => handleRemoveItem(item.productId)} />
          </View>
        )}
      />
      <Button title="Clear Cart" onPress={handleClearCart} />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16,
  },
  item: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#ccc',
  },
});

export default CartScreen;
