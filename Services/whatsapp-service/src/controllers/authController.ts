import { Request, Response } from 'express';
import { authService } from '../services/authService';

export const authController = {
  register: async (req: Request, res: Response) => {
    try {
      const { email, password } = req.body;
      const user = await authService.register(email, password);
      res.status(201).json(user);
    } catch (error: any) {
      res.status(400).json({ message: error.message });
    }
  },

  login: async (req: Request, res: Response) => {
    try {
      const { email, password } = req.body;
      const data = await authService.login(email, password);
      res.json(data);
    } catch (error: any) {
      res.status(401).json({ message: error.message });
    }
  },
};
