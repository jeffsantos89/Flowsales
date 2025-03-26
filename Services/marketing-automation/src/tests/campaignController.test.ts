import request from 'supertest';
import app from '../app';

describe('Campaign Controller', () => {
  it('should create a campaign', async () => {
    const response = await request(app)
      .post('/campaign')
      .send({ name: 'Nova Campanha' });
    
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('name', 'Nova Campanha');
  });
});
