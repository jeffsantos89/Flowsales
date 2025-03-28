export class ConfigError extends Error {
  public code: string;

  constructor(message: string, code: string = 'CONFIG_ERROR') {
    super(message);
    this.name = 'ConfigError';
    this.code = code;

    // Preserve the stack trace (only available in V8 engines)
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, ConfigError);
    }
  }

  public toString(): string {
    return `${this.name} [${this.code}]: ${this.message}`;
  }
}