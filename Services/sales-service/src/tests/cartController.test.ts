import request from 'supertest';
import app from '../app';

describe('Cart Controller Tests', () => {
  it('should add product to cart', async () => {
    const res = await request(app)
      .post('/api/cart')
      .send({
        productId: 1,
        quantity: 2,
      });

    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('products');
  });

  it('should get cart for a user', async () => {
    const res = await request(app).get('/api/cart');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('products');
  });

  it('should remove product from cart', async () => {
    const res = await request(app).delete('/api/cart/1');
    expect(res.status).toBe(204);
  });

  it('should clear cart for a user', async () => {
    const res = await request(app).delete('/api/cart');
    expect(res.status).toBe(204);
  });
});
