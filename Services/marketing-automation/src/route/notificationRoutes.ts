// src/routes/notificationRoutes.ts
import { Router } from 'express';
import { sendUserNotification } from '../controllers/notificationController';
import { authMiddleware } from '../middlewares/authMiddleware';

const router = Router();

router.post('/send', authMiddleware, sendUserNotification);

export default router;
