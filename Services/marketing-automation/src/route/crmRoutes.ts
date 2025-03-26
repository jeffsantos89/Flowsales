// src/routes/crmRoutes.ts
import { Router } from 'express';
import { syncCRM } from '../controllers/crmIntegrationController';
import { authMiddleware } from '../middlewares/authMiddleware';

const router = Router();

router.post('/sync', authMiddleware, syncCRM);

export default router;
