import { Request, Response } from 'express';
import { User } from '../entities/User';
import { AppDataSource } from '../config/db';

const userRepository = AppDataSource.getRepository(User);

export const userController = {
  getProfile: async (req: Request, res: Response) => {
    const userId = req.user?.id;
    const user = await userRepository.findOneBy({ id: userId ? parseInt(userId) : undefined });
    res.json(user);
  },
};
