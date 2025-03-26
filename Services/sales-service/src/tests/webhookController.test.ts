import request from 'supertest';
import app from '../app';

describe('Webhook Controller Tests', () => {
  it('deve processar um webhook com sucesso', async () => {
    const res = await request(app).post('/api/webhooks/receive').send({
      eventType: 'order_created',
      payload: { orderId: '1234', total: 100 },
    });
    expect(res.status).toBe(200);
    expect(res.body.message).toBe('Webhook recebido com sucesso');
  });

  it('deve listar eventos de webhooks', async () => {
    const res = await request(app).get('/api/webhooks/events');
    expect(res.status).toBe(200);
    expect(res.body).toBeInstanceOf(Array);
  });
});
