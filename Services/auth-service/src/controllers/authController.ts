import { Request, Response } from 'express';
import { authenticateWithMFA } from '../services/auth/authService';

export const loginHandler = async (req: Request, res: Response) => {
  try {
    const { username, password, mfaToken } = req.body;
    const result = await authenticateWithMFA(username, password, mfaToken);
    return res.json(result);
  } catch (err) {
    return res.status(401).json({ error: err.message });
  }
};
