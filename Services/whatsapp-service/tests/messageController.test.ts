import request from 'supertest';
import appInstance from '../src/index';
import { describe, it } from 'node:test';
import { expect } from '@jest/globals';
import express from 'express';
const app = express();

// ... rest of your configurations

const server = appInstance.listen();
export default server;

describe('Message Controller', () => {
  it('Deve retornar 200 e a mensagem enviada', async () => {
    const res = await request(app)
      .post('/api/messages/send')
      .send({
        number: '555199999999',
        message: 'Olá!'
      });
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty('status', 'success');
  });
});

