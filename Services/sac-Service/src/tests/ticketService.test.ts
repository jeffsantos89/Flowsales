import * as request from 'supertest';
import { app } from '../index';
// import jest from 'jest'; // jest is globally available

describe('Testes para o SAC Service', () => {
  it('Deve criar um novo ticket', async () => {
    const response = await request(app).post('/api/tickets').send({
      title: 'Problema no pedido',
      description: 'O pedido não chegou conforme combinado.',
    });
    expect(response.status).toBe(201);
    expect(response.body.title).toBe('Problema no pedido');
  });
});
import { createTicket } from '../services/ticketService';
import { Ticket } from '../models/ticketModel';
import { sendNotification } from '../services/notificationService';

jest.mock('../services/notificationService');

describe('Ticket Service', () => {
  it('Deve criar um ticket com sucesso', async () => {
    const spy = jest.spyOn(Ticket.prototype, 'save').mockResolvedValueOnce({ id: '1', title: 'Teste', description: 'Descrição' });
    await createTicket('Teste', 'Descrição');
    expect(spy).toHaveBeenCalled();
    expect(sendNotification).toHaveBeenCalledWith(expect.objectContaining({ email: 'suporte@empresa.com' }));
  });
});
