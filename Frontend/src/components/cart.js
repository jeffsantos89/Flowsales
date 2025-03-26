import React, { useEffect, useState } from 'react';

function Cart() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const sessionId = 'abc123'; // Sessão fictícia
    const fetchCart = async () => {
      try {
        const apiUrl = process.env.REACT_APP_API_URL;
        const res = await fetch(`${apiUrl}/cart?session_id=${sessionId}`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${process.env.REACT_APP_API_TOKEN}`
          }
        });
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        const data = await res.json();
        setItems(data);
      } catch (err) {
        console.error('Erro ao buscar carrinho:', err);
        setError('Erro ao buscar carrinho. Tente novamente mais tarde.');
      } finally {
        setLoading(false);
      }
    };
    fetchCart();
  }, []);

  if (loading) {
    return <div>Carregando...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  return (
    <div style={{ margin: '20px' }}>
      <h2>Carrinho</h2>
      <ul>
        {items.map((it) => (
          <li key={it.id}>
            Produto ID: {it.product_id}, Quantidade: {it.quantity}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Cart;