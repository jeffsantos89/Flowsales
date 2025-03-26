import { NextFunction, Request, Response } from 'express';
import { affiliateRepository } from '../repositories/affiliateRepository';
import { ApiError } from '../utils/apiError';
import { validateAffiliateInput } from '../utils/validator';
import logger from '../utils/logger';
import { ValidationError } from '../utils/errors';

export const registerAffiliate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    validateAffiliateInput(req.body);
    const affiliate = await affiliateRepository.createAffiliate(req.body);
    logger.info('Affiliate registered successfully', {
      affiliateId: affiliate.id,
    });

    res.status(201).json({
      message: 'Affiliate registered successfully',
      affiliate,
    });
  } catch (error) {
    if (error instanceof ValidationError) {
      return res
        .status(400)
        .json({ error: 'Invalid data', details: error.details });
    }
    next(new ApiError(500, 'Failed to register affiliate', error));
  }
};

export const getAffiliate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const affiliate = await affiliateRepository.getAffiliateById(
      Number(req.params.id)
    );
    if (!affiliate) {
      throw new ApiError(404, 'Affiliate not found');
    }
    res.status(200).json(affiliate);
  } catch (error) {
    next(error);
  }
};

export const listAffiliates = async (
  _req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const affiliates = await affiliateRepository.getAllAffiliates();
    logger.info('Fetched affiliates list', { count: affiliates.length });

    res.status(200).json({
      total: affiliates.length,
      data: affiliates,
    });
  } catch (error) {
    next(new ApiError(500, 'Failed to fetch affiliates', error));
  }
};
