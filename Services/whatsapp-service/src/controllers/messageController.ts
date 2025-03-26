import { Request, Response } from 'express';
import { whatsappApiService } from '../services/whatsappApiService';

export const messageController = {
  sendMessage: async (req: Request, res: Response) => {
    try {
      const { number, message } = req.body;
      const response = await whatsappApiService.sendMessage(number, message);
      res.json({ status: 'success', response });
    } catch (error) {
      res.status(500).json({ status: 'error', message: error.message });
    }
  },

  getHistory: async (req: Request, res: Response) => {
    try {
      const history = await whatsappApiService.getHistory();
      res.json({ status: 'success', history });
    } catch (error) {
      res.status(500).json({ status: 'error', message: error.message });
    }
  }
};
