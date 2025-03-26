import request from 'supertest';
import app from '../src/app';

describe('Integration Tests', () => {
  it('should return analytics data', async () => {
    const response = await request(app).get('/api/analytics');
    expect(response.status).toBe(200);
    expect(response.body).toBeDefined();
  });
});
