import React, { useState } from 'react';

function Checkout() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleCheckout() {
    setLoading(true);
    setError(null);

    try {
      const apiUrl = process.env.REACT_APP_API_URL;
      const sessionId = "abc";

      const response = await fetch(`${apiUrl}/checkout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();
      console.log('Checkout successful:', data);
    } catch (error) {
      console.error('Checkout failed:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button onClick={handleCheckout} disabled={loading}>
        {loading ? 'Processing...' : 'Checkout'}
      </button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default Checkout;