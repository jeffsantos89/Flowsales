import request from 'supertest';
import app from '../app';

describe('Notification Controller Tests', () => {
  it('deve enviar um email com sucesso', async () => {
    const res = await request(app).post('/api/notifications/email').send({
      to: 'test@example.com',
      subject: 'Teste de Email',
      message: 'Este é um teste de email',
    });
    expect(res.status).toBe(200);
    expect(res.body.message).toBe('Email enviado com sucesso!');
  });

  it('deve enviar um SMS com sucesso', async () => {
    const res = await request(app).post('/api/notifications/sms').send({
      to: '+1234567890',
      message: 'Este é um teste de SMS',
    });
    expect(res.status).toBe(200);
    expect(res.body.message).toBe('SMS enviado com sucesso!');
  });
});
