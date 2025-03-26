// src/controllers/campaignController.ts
import { Request, Response } from 'express';
import { createCampaign, getCampaigns } from '../services/campaignService';
import { responseHandler } from '../utils/responseHandler';

export const getAllCampaigns = async (req: Request, res: Response) => {
  try {
    const campaigns = await getCampaigns();
    responseHandler(res, 200, 'Campaigns fetched successfully', campaigns);
  } catch (error) {
    responseHandler(res, 500, 'Error fetching campaigns', { error: error.message });
  }
};

export const createNewCampaign = async (req: Request, res: Response) => {
  try {
    const campaign = await createCampaign(req.body);
    responseHandler(res, 201, 'Campaign created successfully', campaign);
  } catch (error) {
    responseHandler(res, 500, 'Error creating campaign', { error: error.message });
  }
};
