import { Request, Response, NextFunction } from 'express';
import morgan from 'morgan';

export const requestLogger = morgan('dev');
