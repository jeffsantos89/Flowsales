// src/tests/e2e/campaignFlow.test.ts
import request from 'supertest';
import app from '../../app';

describe('Campaign Flow', () => {
  it('should create a campaign', async () => {
    const response = await request(app)
      .post('/api/campaigns')
      .send({
        name: 'Black Friday',
        target: '1000 users',
      });
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });

  it('should list campaigns', async () => {
    const response = await request(app).get('/api/campaigns');
    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });
});
