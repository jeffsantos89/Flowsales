import { Request, Response, NextFunction } from 'express';
import { hasPermission } from '../services/rbac/rbacService';
import { logger } from '../utils/logger';

// Tipos
type Permission = string;
type UserRole = string;
type UserId = string;

interface AuthenticatedUser {
  role: UserRole;
  id: UserId;
}

interface AuthenticatedRequest extends Request {
  user?: AuthenticatedUser;
}

// Enums para códigos de status HTTP
enum HttpStatus {
  OK = 200,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  INTERNAL_SERVER_ERROR = 500,
}

// Error handling
export class RBACError extends Error {
  constructor(
    message: string,
    public readonly statusCode: HttpStatus = HttpStatus.FORBIDDEN,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'RBACError';
    Error.captureStackTrace(this, this.constructor);
  }
}

// Tipos de resposta de erro
interface ErrorResponse {
  error: string;
  timestamp: string;
  path: string;
  traceId?: string;
  details?: unknown;
}

// Classe principal RBAC
export class RBACMiddleware {
  private static generateTraceId(): string {
    return `rbac-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  private static createErrorResponse(
    error: RBACError,
    path: string,
    traceId: string
  ): ErrorResponse {
    return {
      error: error.message,
      timestamp: new Date().toISOString(),
      path,
      traceId,
      details: error.details,
    };
  }

  private static async validatePermissions(
    user: AuthenticatedUser,
    permissions: Permission[],
    traceId: string
  ): Promise<void> {
    logger.debug('Checking permissions', {
      userId: user.id,
      role: user.role,
      permissions,
      traceId,
    });

    const permissionChecks = permissions.map(permission =>
      hasPermission(user.role, permission)
    );

    const results = await Promise.all(permissionChecks);
    const hasAllPermissions = results.every(result => result);

      if (!hasAllPermissions) {
        logger.warn('Access denied', {
          userId: user.id,
          permissions,
          traceId,
          userRole: user.role
        });
        throw new RBACError('Insufficient permissions', HttpStatus.FORBIDDEN);
      }
  }

  public static checkPermission(requiredPermissions: Permission | Permission[]) {
    return async (
      req: AuthenticatedRequest,
      res: Response,
      next: NextFunction
    ): Promise<void> => {
      const traceId = this.generateTraceId();

      try {
        if (!req.user) {
          throw new RBACError('Unauthorized - No user found', HttpStatus.UNAUTHORIZED);
        }

        const permissions = Array.isArray(requiredPermissions)
          ? requiredPermissions
          : [requiredPermissions];

        await this.validatePermissions(req.user, permissions, traceId);

        logger.debug('Permission granted', {
          userId: req.user.id,
          traceId,
        });

        next();
      } catch (error) {
        const rbacError =
          error instanceof RBACError
            ? error
            : new RBACError(
                'Internal Server Error',
                HttpStatus.INTERNAL_SERVER_ERROR,
                error
              );

        logger.error('RBAC Error', {
          error,
          traceId,
          path: req.path
        });

        res
          .status(rbacError.statusCode)
          .json(this.createErrorResponse(rbacError, req.path, traceId));
      }
    };
  }

  public static hasPermission(...permissions: Permission[]) {
    return this.checkPermission(permissions);
  }
}
