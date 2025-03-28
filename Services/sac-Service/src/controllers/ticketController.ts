import { NextFunction, Request, Response } from 'express';
import { z } from 'zod';
import { createTicket, createTicket as createTicketService } from '../services/ticketService'; // Supondo que você tenha um serviço para criar tickets
import { title } from 'process';

// Define o schema de validação
const ticketSchema = z.object({
  title: z.string().min(5, 'Título muito curto'),
  description: z.string().min(10, 'Descrição muito curta'),
});

// Middleware para validação de tickets
export const validateTicket = (req: Request, res: Response, next: NextFunction) => {
  try {
    req.body = ticketSchema.parse(req.body);
    next();
  } catch (error) {
    res.status(400).json({ message: error.errors ?? 'Erro na validação do ticket' });
  }
};

// Função para criação de tickets
// Removida a função duplicada createTicket

// Controlador para criação de tickets
export const createTicketController = async (req: Request, res: Response) => {
  const { title, description } = req.body;
  try {
    const ticket = await createTicket(title, description);
    res.status(201).json(ticket);
  } catch (error) {
    const ticket = await createTicketService(title, description);
  }
};
