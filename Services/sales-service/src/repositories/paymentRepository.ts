import { AppDataSource } from '../config/database';
import { Payment } from '../entities/Payment';

export const paymentRepository = AppDataSource.getRepository(Payment);
