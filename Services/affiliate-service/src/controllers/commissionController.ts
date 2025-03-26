import { NextFunction, Request, Response } from 'express';
import {
  createCommission,
  getCommissions,
} from '../services/commissionService';
import logger from '../utils/logger';
import { validateCommissionInput } from '../utils/validator';
import { DatabaseError, ValidationError } from '../utils/errors';
import { ApiError } from '../utils/apiError';
import { commissionRepository } from '../repositories/commissionRepository';

// Adicionar nova comissão
export const addCommission = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const span = req.tracer?.startSpan('addCommission'); // OpenTelemetry (opcional)
  try {
    validateCommissionInput(req.body); // validação explícita dos dados
    const commission = await createCommission(req.body);

    logger.info('Commission added successfully', {
      commissionId: commission.id,
    });

    res.status(201).json({
      message: 'Commission added successfully',
      commission,
    });
  } catch (error: unknown) {
    logger.error('Error adding commission', { error });

    if (error instanceof ValidationError) {
      return res
        .status(400)
        .json({ message: error.message, details: error.details });
    }

    if (error instanceof DatabaseError) {
      return res
        .status(503)
        .json({ message: 'Database error', details: error.message });
    }

    next(error); // Middleware global
  } finally {
    span?.end();
  }
};

// Listar todas as comissões
export const listCommissions = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const span = req.tracer?.startSpan('listCommissions'); // OpenTelemetry (opcional)

  try {
    const commissions = await getCommissions();

    logger.info('Commissions fetched successfully', {
      count: commissions.length,
    });

    res.status(200).json({
      message: 'Commissions retrieved successfully',
      count: commissions.length,
      commissions,
    });
  } catch (error: unknown) {
    logger.error('Error fetching commissions', { error });

    if (error instanceof DatabaseError) {
      return res
        .status(503)
        .json({ message: 'Database error', details: error.message });
    }

    next(error); // Middleware global
  } finally {
    span?.end();
  }
};

export const getCommission = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const commission = await commissionRepository.getCommissionById(
      Number(req.params.id)
    );
    if (!commission) {
      throw new ApiError(404, 'Commission not found');
    }
    res.status(200).json(commission);
  } catch (error) {
    next(error);
  }
};
