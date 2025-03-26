export class ValidationError extends Error {
  details: Record<string, unknown>;
  constructor(message: string, details?: Record<string, unknown>) {
    super(message);
    this.name = 'ValidationError';
    this.details = details || {};
    Error.captureStackTrace(this, this.constructor);
  }
}

export class DatabaseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'DatabaseError';
  }
}

export class AuthenticationError extends Error {
  public statusCode: number;

  constructor(message = 'Authentication Failed', statusCode = 401) {
    super(message);
    this.name = 'AuthenticationError';
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class AuthorizationError extends Error {
  public statusCode: number;

  constructor(message = 'Access Denied', statusCode = 403) {
    super(message);
    this.name = 'AuthorizationError';
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}

export class NotFoundError extends Error {
  public statusCode: number;

  constructor(message = 'Resource Not Found', statusCode = 404) {
    super(message);
    this.name = 'NotFoundError';
    this.statusCode = statusCode;
    Error.captureStackTrace(this, this.constructor);
  }
}
