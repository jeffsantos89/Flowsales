import { redisClient } from '../config/redisConfig';
import { Ticket } from '../models/ticketModel'; // Certifique-se de importar o modelo Ticket
import { logger } from '../utils/logger'; // Supondo que você tenha um utilitário de logging
import * as dotenv from 'dotenv';

dotenv.config();

const CACHE_EXPIRATION = process.env.CACHE_EXPIRATION || 300; // 5 minutos por padrão

export const getTicketById = async (ticketId: string) => {
  try {
    const cacheKey = `ticket:${ticketId}`;
    const cachedTicket = await redisClient.get(cacheKey);

    if (cachedTicket) {
      logger.info(`Cache hit for ticket ${ticketId}`);
      return JSON.parse(cachedTicket);
    }

    const ticket = await Ticket.findById(ticketId);
    if (ticket) {
      await redisClient.set(cacheKey, JSON.stringify(ticket), 'EX', CACHE_EXPIRATION);
    }

    return ticket;
  } catch (error) {
    logger.error(`Error fetching ticket ${ticketId}: ${error.message}`);
    throw new Error('Error fetching ticket');
  }
};

export const createTicket = async (title: string, description: string) => {
  try {
    // Implementação da lógica para criar um ticket
    const newTicket = new Ticket({ title, description });
    await newTicket.save();

    // Opcional: Invalide o cache se necessário
    // await redisClient.del(`tickets`);

    return newTicket;
  } catch (error) {
    logger.error(`Error creating ticket: ${error.message}`);
    throw new Error('Error creating ticket');
  }
};
