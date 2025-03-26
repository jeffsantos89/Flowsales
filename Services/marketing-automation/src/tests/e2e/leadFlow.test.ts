import request from 'supertest';
import app from '../app';

describe('Lead Flow', () => {
  it('should create a new lead', async () => {
    const response = await request(app)
      .post('/api/leads')
      .send({
        name: 'Test Lead',
        email: 'test@example.com',
        source: 'API Test',
      });
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });

  it('should fetch leads', async () => {
    const response = await request(app).get('/api/leads');
    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });
});
