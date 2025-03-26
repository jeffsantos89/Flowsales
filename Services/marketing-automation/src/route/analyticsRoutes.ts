// src/routes/analyticsRoutes.ts
import { Router } from 'express';
import { getChurnPrediction } from '../controllers/analyticsController';
import { authMiddleware } from '../middlewares/authMiddleware';

const router = Router();

router.get('/predict-churn/:leadId', authMiddleware, getChurnPrediction);

export default router;
