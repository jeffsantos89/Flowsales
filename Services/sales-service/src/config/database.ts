import 'reflect-metadata';
import { DataSource } from 'typeorm';
import { Order } from '../entities/Order';
import { Cart } from '../entities/Cart';
import { Payment } from '../entities/Payment';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: process.env.DB_HOST,
  port: Number(process.env.DB_PORT),
  username: process.env.DB_USER,
  password: process.env.DB_PASS,
  database: process.env.DB_NAME,
  synchronize: true,
  logging: false,
  entities: [Order, Cart, Payment],
});
