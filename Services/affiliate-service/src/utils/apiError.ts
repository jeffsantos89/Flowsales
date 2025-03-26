export class ApiError extends Error {
  public readonly statusCode: number;
  public readonly originalError?: unknown;

  constructor(statusCode: number, message: string, originalError?: unknown) {
    super(message);
    this.statusCode = statusCode;
    this.originalError = originalError;

    // Corrige problema de herança em TypeScript
    Object.setPrototypeOf(this, new.target.prototype);

    // Captura stack trace para debugging
    Error.captureStackTrace(this);
  }

  /**
   * Método auxiliar para criar um erro de requisição inválida (400)
   */
  static badRequest(message: string, originalError?: unknown): ApiError {
    return new ApiError(400, message, originalError);
  }

  /**
   * Método auxiliar para criar um erro de não autorizado (401)
   */
  static unauthorized(
    message = 'Unauthorized',
    originalError?: unknown
  ): ApiError {
    return new ApiError(401, message, originalError);
  }

  /**
   * Método auxiliar para criar um erro de permissão negada (403)
   */
  static forbidden(message = 'Forbidden', originalError?: unknown): ApiError {
    return new ApiError(403, message, originalError);
  }

  /**
   * Método auxiliar para criar um erro de recurso não encontrado (404)
   */
  static notFound(message = 'Not Found', originalError?: unknown): ApiError {
    return new ApiError(404, message, originalError);
  }

  /**
   * Método auxiliar para criar um erro interno do servidor (500)
   */
  static internal(
    message = 'Internal Server Error',
    originalError?: unknown
  ): ApiError {
    return new ApiError(500, message, originalError);
  }

  /**
   * Método para lidar com erros inesperados no sistema
   */
  static handleError(error: unknown): never {
    // TODO: Replace with proper logging system
    // const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    // console.error(`Error occurred: ${errorMessage}`);
    throw ApiError.internal('An unexpected error occurred', error);
  }
}
