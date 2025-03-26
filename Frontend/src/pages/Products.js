import React, { useEffect, useState, useCallback } from 'react';
import { useApi } from '../services/api';

function Products() {
  const api = useApi();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get('/products');
      setProducts(res.data);
    } catch (err) {
      setError('Erro ao buscar produtos');
      console.error('Erro ao buscar produtos', err);
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div style={{ margin: 20 }}>
      <h2>Lista de Produtos</h2>
      <ul>
        {products.map((product) => (
          <li key={product.id}>
            {product.name} - R$ {product.price}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Products;
