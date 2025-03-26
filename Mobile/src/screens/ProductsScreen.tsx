import React, { useEffect, useState } from 'react';
import { View, Text, Button, FlatList, TouchableOpacity, StyleSheet } from 'react-native';
import { api } from '../services/api';
import { useDispatch } from 'react-redux';
import { logoutThunk } from '../store/slices/authSlice';
import { AppDispatch } from '../store';

export default function ProductsScreen() {
  const [products, setProducts] = useState<any[]>([]);
  const dispatch = useDispatch<AppDispatch>();

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const res = await api.get('/products');
        setProducts(res.data);
      } catch (err) {
        console.error('Erro ao obter produtos:', err);
      }
    };
    fetchProducts();
  }, []);

  const handleLogout = () => {
    dispatch(logoutThunk());
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Lista de Produtos</Text>
        <Button title="Sair" onPress={handleLogout} />
      </View>
      <FlatList
        data={products}
        keyExtractor={(item) => String(item.id)}
        renderItem={({ item }) => (
          <TouchableOpacity style={styles.item}>
            <Text>{item.name}</Text>
            <Text>R$ {item.price}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 24 },
  header: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 16 },
  title: { fontSize: 20 },
  item: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#eef',
    padding: 12,
    marginBottom: 8,
    borderRadius: 8
  }
});
