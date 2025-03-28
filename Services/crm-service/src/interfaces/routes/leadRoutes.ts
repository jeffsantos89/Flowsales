import { Router } from 'express';
import { createLeadHandler } from '../controllers/leadController';

const router = Router();
router.post('/leads', createLeadHandler);

export default router;
