// src/controllers/analyticsController.ts
import { Request, Response } from 'express';
import { predictChurn } from '../services/analyticsService';
import { responseHandler } from '../utils/responseHandler';

export const getChurnPrediction = async (req: Request, res: Response) => {
  try {
    const { leadId } = req.params;
    const prediction = await predictChurn(Number(leadId));
    responseHandler(res, 200, 'Churn prediction calculated successfully', { prediction });
  } catch (error) {
    responseHandler(res, 500, 'Error calculating churn prediction', { error: error.message });
  }
};
