import { Router } from 'express';
import { createTicketController } from '../controllers/ticketController';

const router = Router();

router.post('/tickets', createTicketController);

export default router;
