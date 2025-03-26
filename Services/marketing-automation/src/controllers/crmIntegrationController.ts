// src/controllers/crmIntegrationController.ts
import { Request, Response } from 'express';
import { syncCRMData } from '../services/crmIntegrationService';
import { responseHandler } from '../utils/responseHandler';

export const syncCRM = async (req: Request, res: Response) => {
  try {
    await syncCRMData();
    responseHandler(res, 200, 'CRM data synchronized successfully');
  } catch (error) {
    responseHandler(res, 500, 'Error synchronizing CRM data', { error: error.message });
  }
};
