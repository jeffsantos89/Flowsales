import { Request, Response } from 'express';
import { processPayment, confirmPaymentStatus } from '../services/paymentService';

export const initiatePayment = async (req: Request, res: Response) => {
  try {
    const paymentData = await processPayment(req.body);
    res.status(200).json(paymentData);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const confirmPayment = async (req: Request, res: Response) => {
  try {
    const confirmation = await confirmPaymentStatus(req.body);
    res.status(200).json(confirmation);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
