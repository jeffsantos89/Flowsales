// src/tests/e2e/leadFlow.test.ts
import request from 'supertest';
import app from '../../app';

describe('Lead Flow', () => {
  it('should create a new lead', async () => {
    const response = await request(app)
      .post('/api/leads')
      .send({
        name: 'John Doe',
        email: 'john@example.com',
      });
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });

  it('should get leads', async () => {
    const response = await request(app).get('/api/leads');
    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });
});
