import { Router } from 'express';
import { authMiddleware } from '../middlewares/authMiddleware';
import { userController } from '../controllers/userController';
import { Request, Response, NextFunction } from 'express';

const router = Router();

userController.getProfile = async (req: Request, res: Response): Promise<void> => {
    res.json({ message: 'Profile data' });
};

router.get('/me', authMiddleware, userController.getProfile);

export default router;
