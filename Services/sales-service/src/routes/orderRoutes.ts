import { Router } from 'express';
import { addOrder } from '../controllers/orderController';

const router = Router();

router.post('/create', addOrder);

export default router;
