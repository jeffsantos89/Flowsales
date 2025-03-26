import request from 'supertest';
import app from '../../../app';
import { expect } from '@jest/globals';

describe('Commission Controller', () => {
  let authToken: string;

  // Antes de todos os testes, realiza login para obter token
  beforeAll(async () => {
    const res = await request(app).post('/api/auth/login').send({
      email: 'admin@example.com',
      password: 'password123',
    });
    authToken = res.body.token;
  });

  // Teste de sucesso para adicionar comissão
  it('should add a new commission successfully', async () => {
    const res = await request(app)
      .post('/api/commissions/add')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        amount: 50,
        status: 'approved',
        affiliateId: 1,
      });

    expect(res.status).toBe(201);
    expect(res.body.message).toBe('Commission added successfully');
    expect(res.body).toHaveProperty('commission');
    expect(res.body.commission).toHaveProperty('id');
    expect(res.body.commission).toHaveProperty('amount', 50);
  });

  // Teste para listar todas as comissões
  it('should list all commissions', async () => {
    const res = await request(app)
      .get('/api/commissions/')
      .set('Authorization', `Bearer ${authToken}`);

    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBeTruthy();
    if (res.body.length > 0) {
      expect(res.body[0]).toHaveProperty('id');
      expect(res.body[0]).toHaveProperty('amount');
      expect(res.body[0]).toHaveProperty('status');
    }
  });

  // Teste para comissão com afiliado inexistente
  it('should return 404 if affiliate does not exist', async () => {
    const res = await request(app)
      .post('/api/commissions/add')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        amount: 50,
        status: 'approved',
        affiliateId: 9999, // ID inexistente
      });

    expect(res.status).toBe(404);
    expect(res.body).toHaveProperty('error', 'Affiliate not found');
  });

  // Teste para valores inválidos (ex.: valor negativo)
  it('should return 400 for invalid commission amount', async () => {
    const res = await request(app)
      .post('/api/commissions/add')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        amount: -50,
        status: 'approved',
        affiliateId: 1,
      });

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('error', 'Invalid amount');
  });

  // Teste para status inválido
  it('should return 400 for invalid status', async () => {
    const res = await request(app)
      .post('/api/commissions/add')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        amount: 50,
        status: 'invalid-status',
        affiliateId: 1,
      });

    expect(res.status).toBe(400);
    expect(res.body).toHaveProperty('error', 'Invalid status');
  });

  // Teste para falta de autenticação (401)
  it('should return 401 if no token is provided', async () => {
    const res = await request(app).post('/api/commissions/add').send({
      amount: 50,
      status: 'approved',
      affiliateId: 1,
    });

    expect(res.status).toBe(401);
    expect(res.body).toHaveProperty('error', 'Access denied');
  });

  // Teste para erro de conexão com o banco de dados
  it('should handle database connection error gracefully', async () => {
    const res = await request(app)
      .post('/api/commissions/add')
      .set('Authorization', `Bearer ${authToken}`)
      .set('X-Simulate-DB-Error', 'true') // Cabeçalho hipotético para simular erro
      .send({
        amount: 50,
        status: 'approved',
        affiliateId: 1,
      });

    expect(res.status).toBe(500);
    expect(res.body).toHaveProperty('error', 'Database connection error');
  });
});
