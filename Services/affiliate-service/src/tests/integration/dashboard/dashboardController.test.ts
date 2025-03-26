import request from 'supertest';
import app from '../../../app';
import { beforeAll, describe, expect, it } from '@jest/globals';

describe('Dashboard Controller', () => {
  let authToken: string;

  // Login antes dos testes para obter um token válido
  beforeAll(async () => {
    const res = await request(app).post('/api/auth/login').send({
      email: 'johndoe@example.com',
      password: 'Password123!',
    });
    authToken = res.body.token;
  });

  // Teste para obter dados do dashboard com sucesso
  it('should fetch dashboard data successfully', async () => {
    const res = await request(app)
      .get('/api/dashboard/')
      .set('Authorization', `Bearer ${authToken}`);

    expect(res.status).toBe(200);
    expect(res.body).toMatchObject({
      totalAffiliates: expect.any(Object),
      totalCommissions: expect.any(Object),
      totalEarnings: expect.any(Object),
    });
    expect(typeof res.body.totalAffiliates).toBe('number');
    expect(typeof res.body.totalCommissions).toBe('number');
    expect(typeof res.body.totalEarnings).toBe('number');
  });

  // Teste para verificar erro 401 (não autorizado) se o token estiver ausente
  it('should return 401 if token is missing', async () => {
    const res = await request(app).get('/api/dashboard/');
    expect(res.status).toBe(401);
    expect(res.body).toHaveProperty('error', 'Access denied');
  });

  // Teste para erro no servidor (500)
  it('should handle server errors gracefully', async () => {
    const res = await request(app)
      .get('/api/dashboard?forceError=true') // Parâmetro fictício para simular erro
      .set('Authorization', `Bearer ${authToken}`);

    expect(res.status).toBe(500);
    expect(res.body).toHaveProperty('message', 'Internal Server Error');
  });
});
