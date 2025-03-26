import request from 'supertest';
import { expect } from '@jest/globals';
import app from '../../../app';
import { AppDataSource } from '../../../config/database';
import { affiliateRepository } from '../../../repositories/affiliateRepository';
import { Affiliate } from '../../../entities/Affiliate';

describe('Affiliate Controller', () => {
  // Conexão com o banco antes de todos os testes
  beforeAll(async () => {
    await AppDataSource.initialize();
  });

  // Limpar a tabela de afiliados antes de cada teste
  beforeEach(async () => {
    ({});
  });

  // Fechar a conexão com o banco após todos os testes
  afterAll(async () => {
    await AppDataSource.destroy();
  });

  it('should register a new affiliate', async () => {
    const res = await request(app).post('/api/affiliates/register').send({
      name: 'Test Affiliate',
      email: 'test@example.com',
      password: 'password123',
    });

    expect(res.status).toBe(201);
    expect(res.body.message).toBe('Affiliate registered successfully');
    expect(res.body.affiliate).toHaveProperty('id');
    expect(res.body.affiliate).toHaveProperty('name', 'Test Affiliate');
    expect(res.body.affiliate).toHaveProperty('email', 'test@example.com');
    expect(res.body.affiliate).not.toHaveProperty('password');
  });

  it('should not register affiliate with duplicate email', async () => {
    affiliateRepository.save({
      name: 'Test Affiliate',
      email: 'test@example.com',
      password: 'password123',
    });

    const res = await request(app).post('/api/affiliates/register').send({
      name: 'Another Affiliate',
      email: 'test@example.com',
      password: 'password456',
    });

    expect(res.status).toBe(400);
    expect(res.body.message).toBe('Email already exists');
  });

  it('should return error for missing fields', async () => {
    const res = await request(app).post('/api/affiliates/register').send({
      email: 'test@example.com',
      password: 'password123',
    });

    expect(res.status).toBe(400);
    expect(res.body.message).toBe('Validation error');
  });

  it('should encrypt password before saving', async () => {
    await request(app).post('/api/affiliates/register').send({
      name: 'Test Affiliate',
      email: 'secure@example.com',
      password: 'password123',
    });
    const savedAffiliate: Affiliate | null =
      await affiliateRepository.findOneBy({
        email: 'secure@example.com',
      });

    expect(savedAffiliate).not.toBeNull();
    expect(savedAffiliate?.password).not.toBe('password123');
  });

  it('should get a list of affiliates', async () => {
    await affiliateRepository.save([
      {
        name: 'Affiliate 1',
        email: 'affiliate1@example.com',
        password: 'password123',
      },
      {
        name: 'Affiliate 2',
        email: 'affiliate2@example.com',
        password: 'password456',
      },
    ]);

    const res = await request(app).get('/api/affiliates');

    expect(res.status).toBe(200);
    expect(res.body).toBeInstanceOf(Array);
    expect(res.body.length).toBe(2);
    expect(res.body[0]).toHaveProperty('email', 'affiliate1@example.com');
  });
});
