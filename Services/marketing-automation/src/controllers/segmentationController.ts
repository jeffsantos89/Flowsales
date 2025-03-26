// src/controllers/segmentationController.ts
import { Request, Response } from 'express';
import { createSegment, getSegments } from '../services/segmentationService';
import { responseHandler } from '../utils/responseHandler';

export const getAllSegments = async (req: Request, res: Response) => {
  try {
    const segments = await getSegments();
    responseHandler(res, 200, 'Segments fetched successfully', segments);
  } catch (error) {
    responseHandler(res, 500, 'Error fetching segments', { error: error.message });
  }
};

export const createNewSegment = async (req: Request, res: Response) => {
  try {
    const segment = await createSegment(req.body);
    responseHandler(res, 201, 'Segment created successfully', segment);
  } catch (error) {
    responseHandler(res, 500, 'Error creating segment', { error: error.message });
  }
};
