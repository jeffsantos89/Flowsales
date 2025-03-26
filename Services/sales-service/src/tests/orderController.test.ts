import request from 'supertest';
import app from '../app';

describe('Order Controller Tests', () => {
  it('should create a new order', async () => {
    const res = await request(app)
      .post('/api/orders')
      .send({
        userId: 1,
        products: [{ id: 1, quantity: 2 }],
      });

    expect(res.status).toBe(201);
    expect(res.body.message).toBe('Order created successfully');
  });

  it('should get all orders', async () => {
    const res = await request(app).get('/api/orders');
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('data');
  });
});
