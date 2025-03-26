import { Router } from 'express';
import { messageController } from '../controllers/messageController';
import { authMiddleware } from '../middlewares/authMiddleware';

const router = Router();

router.post('/send', authMiddleware, messageController.sendMessage);
router.get('/history', authMiddleware, messageController.getHistory);

export default router;
