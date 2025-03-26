import { NextFunction, Request, Response } from 'express';
import { getDashboardData } from '../services/dashboardService';
import logger from '../utils/logger';
import { checkUserPermissions } from '../middlewares/authMiddleware';

import { Span, trace } from '@opentelemetry/api';
import { User, UserRole, UserStatus } from '../types/user';

interface RequestWithSpan extends Request {
  req: RequestWithSpan;
  res: Response;
  next: NextFunction;
  span?: Span;
}
export const dashboard = async (
  req: RequestWithSpan,
  res: Response,
  next: NextFunction
) => {
  const span = trace.getTracer('dashboard').startSpan('dashboardDataFetch'); // OpenTelemetry Span

  try {
    // Verifica permissões do usuário
    const user = req.user;
    if (!user) {
      return res.status(401).json({ message: 'User not authenticated' });
    }
    if (!checkUserPermissions(user, 'VIEW_DASHBOARD')) {
      logger.warn('Unauthorized dashboard access attempt', { userId: user.id });
      return res.status(403).json({ message: 'Unauthorized access' });
    }

    const userData: User = {
      ...user,
      name: user.name || '',
      role: (user.role as UserRole) || ('affiliate' as UserRole),
      status: (user.status as UserStatus) || ('active' as UserStatus),
    };
    const data = await getDashboardData(userData);

    logger.info('Dashboard data fetched successfully', {
      userId: user.id,
      dataLength: Object.keys(data).length,
    });

    res.status(200).json({
      message: 'Dashboard data retrieved successfully',
      data,
    });
  } catch (error: unknown) {
    logger.error('Failed to fetch dashboard data', { error });

    // Tratamento específico de erros conhecidos
    if (error instanceof Error && error.name === 'DashboardDataError') {
      return res.status(503).json({
        message: 'Service temporarily unavailable',
        details: error.message,
      });
    }

    next(error); // Middleware global de erro
  } finally {
    span?.end(); // Finaliza o span do OpenTelemetry
  }
};
