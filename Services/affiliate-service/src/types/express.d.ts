import { Tracer } from '@opentelemetry/api';

// Define user roles as an enum for better type safety
enum UserRole {
  ADMIN = 'admin',
  AFFILIATE = 'affiliate',
}

// Define user interface for better reusability
interface User {
  sub: string;
  email: string;
  role: UserRole;
  createdAt?: Date;
  lastLogin?: Date;
}

// Define custom error types
interface RequestError extends Error {
  statusCode: number;
  code: string;
}

declare global {
  namespace Express {
    interface Request {
      tracer?: Tracer;
      correlationId?: string;
      user?: User;
      requestStartTime?: number;
      clientIp?: string;
      requestId?: string;
    }

    // Add response interface for completeness
    interface Response {
      error?: RequestError;
    }
  }
}

// Ensure this is treated as a module
export { UserRole, User, RequestError };
