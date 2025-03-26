import jwt from 'jsonwebtoken';
import { NextFunction, Request, Response } from 'express';
import logger from '../utils/logger';
import { UnauthorizedError, ForbiddenError } from '../utils/apiError';

// Enhanced type definitions
declare module 'express' {
  interface Request {
    user?: AuthenticatedUser;
  }
}

export interface AuthenticatedUser {
  id: string;
  userId: string;
  email: string;
  name: string;
  roles: string[];
  permissions: string[];
  exp: number;
  iat: number;
  [key: string]: unknown;
}

interface AuthConfig {
  secret: string;
  algorithm: jwt.Algorithm;
  tokenSource: ('header' | 'cookie' | 'query')[];
}

// Configuration constants
const AUTH_CONFIG: AuthConfig = {
  secret: process.env.JWT_SECRET || '',
  algorithm: 'HS256',
  tokenSource: ['header', 'cookie', 'query'],
};

// Validation at startup
if (!AUTH_CONFIG.secret) {
  throw new Error('JWT_SECRET environment variable is required');
}

export class AuthenticationService {
  private static instance: AuthenticationService;
  private tokenBlacklist: Set<string> = new Set();

  private constructor() {}

  static getInstance(): AuthenticationService {
    if (!AuthenticationService.instance) {
      AuthenticationService.instance = new AuthenticationService();
    }
    return AuthenticationService.instance;
  }

  public blacklistToken(token: string): void {
    this.tokenBlacklist.add(token);
  }

  public isTokenBlacklisted(token: string): boolean {
    return this.tokenBlacklist.has(token);
  }

  public clearBlacklist(): void {
    this.tokenBlacklist.clear();
  }
}

export const authMiddleware = (options: {
  requiredRoles?: string[];
  requiredPermissions?: string[];
}) => {
  const { requiredRoles = [], requiredPermissions = [] } = options;
  const authService = AuthenticationService.getInstance();

  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      const token = extractToken(req);
      if (!token) {
        throw new UnauthorizedError('Authentication token is required');
      }

      if (authService.isTokenBlacklisted(token)) {
        throw new UnauthorizedError('Token has been revoked');
      }

      const decoded = verifyAndDecodeToken(token);
      validateTokenClaims(decoded, { requiredRoles, requiredPermissions });

      req.user = decoded;
      next();
    } catch (error) {
      handleAuthError(error, res);
    }
  };
};

function extractToken(req: Request): string | null {
  for (const source of AUTH_CONFIG.tokenSource) {
    switch (source) {
      case 'header':
        const authHeader = req.headers.authorization;
        if (authHeader?.startsWith('Bearer ')) {
          return authHeader.slice(7);
        }
        break;
      case 'cookie':
        if (req.cookies?.token) {
          return req.cookies.token;
        }
        break;
      case 'query':
        if (req.query.token && typeof req.query.token === 'string') {
          return req.query.token;
        }
        break;
    }
  }
  return null;
}

function verifyAndDecodeToken(token: string): AuthenticatedUser {
  try {
    return jwt.verify(token, AUTH_CONFIG.secret, {
      algorithms: [AUTH_CONFIG.algorithm],
    }) as AuthenticatedUser;
  } catch (error) {
    logger.error('Token verification failed', { error, token: token.slice(0, 10) });
    throw new UnauthorizedError('Invalid or expired token');
  }
}

function validateTokenClaims(
  decoded: AuthenticatedUser,
  { requiredRoles, requiredPermissions }: { requiredRoles: string[]; requiredPermissions: string[] }
): void {
  if (requiredRoles.length > 0 && !requiredRoles.some(role => decoded.roles.includes(role))) {
    throw new ForbiddenError('Insufficient role privileges');
  }

  if (requiredPermissions.length > 0 && !requiredPermissions.some(perm => decoded.permissions.includes(perm))) {
    throw new ForbiddenError('Insufficient permissions');
  }
}

function handleAuthError(error: unknown, res: Response): void {
  logger.error('Authentication error', { error });

  if (error instanceof UnauthorizedError) {
    res.status(401).json({ error: error.message });
  } else if (error instanceof ForbiddenError) {
    res.status(403).json({ error: error.message });
  } else {
    res.status(500).json({ error: 'Internal authentication error' });
  }
}

export function checkUserPermissions(user: unknown, permission: string): boolean {
  if (!user || typeof user !== 'object') return false;
  
  const authenticatedUser = user as AuthenticatedUser;
  return authenticatedUser.permissions?.includes(permission) || 
         authenticatedUser.roles?.includes('admin') || 
         false;
}

export default authMiddleware;
