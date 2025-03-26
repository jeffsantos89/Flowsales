// src/types/winston-logstash-transport.d.ts
declare module 'winston-logstash-transport' {
  import TransportStream from 'winston-transport';
  import { TransportStreamOptions } from 'winston-transport';

  interface LogstashTransportOptions extends TransportStreamOptions {
    // Required fields
    host: string;
    port: number;

    // Optional fields with specific types
    ssl?: boolean;
    maxRetries?: number;
    max_connect_retries?: number;
    timeout_connect_retries?: number;
    retryInterval?: number;
    handleExceptions?: boolean;

    // Additional SSL options
    sslKey?: string;
    sslCert?: string;
    sslCA?: string;

    // Timeout options
    timeout?: number;

    // Buffer options
    bufferSize?: number;
    flushInterval?: number;

    // Additional options for flexibility
    [key: string]: unknown;
  }

  class LogstashTransport extends TransportStream {
    constructor(options: LogstashTransportOptions);

    // Add common methods
    log(info: unknown, callback: () => void): void;
    close(): void;
  }

  export = LogstashTransport;
}
