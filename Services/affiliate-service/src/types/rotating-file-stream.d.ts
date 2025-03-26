declare module 'rotating-file-stream' {
  import { WriteStream } from 'fs';

  interface RotatingFileStreamOptions {
    /** Time interval to rotate the file (e.g., '1d', '1h', '1m') */
    interval?: string;
    /** Directory path where files will be stored */
    path?: string;
    /** Maximum size of each file (e.g., '10M', '1G') */
    size?: string;
    /** Enable/disable file compression */
    compress?: boolean | 'gzip';
    /** Maximum number of rotated files to keep */
    maxFiles?: number;
    /** File mode (permissions) */
    mode?: number;
    /** File ownership */
    owner?: { uid: number; gid: number };
    /** Custom compression options */
    compressionOptions?: {
      level?: number;
      strategy?: number;
    };
    /** Rotation time zone */
    timeZone?: string;
    /** Initial rotation on start */
    initialRotation?: boolean;
    /** Custom rotation function */
    rotate?: (filename: string, index: number) => Promise<void>;
  }

  type FileNameGenerator = string | ((time: Date, index?: number) => string);

  interface RotatingFileStream extends WriteStream {
    /** Manually trigger file rotation */
    rotate(): Promise<void>;
    /** Get current file name */
    getCurrentFileName(): string;
    /** Close the stream and cleanup resources */
    end(cb?: () => void): void;
  }

  function rotatingFileStream(
    filename: FileNameGenerator,
    options?: RotatingFileStreamOptions
  ): RotatingFileStream;

  export = rotatingFileStream;
}
