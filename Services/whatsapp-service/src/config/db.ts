import { DataSource } from 'typeorm';
import { config } from './index';

export const AppDataSource = new DataSource({
  type: 'postgres',
  host: config.postgresHost,
  port: 5432,
  username: config.postgresUser,
  password: config.postgresPassword,
  database: config.postgresDb,
  synchronize: true,
  logging: false,
  entities: ['src/entities/*.ts'],
});

AppDataSource.initialize()
  .then(() => console.log('Conectado ao PostgreSQL!'))
  .catch((error) => console.error('Erro ao conectar ao PostgreSQL:', error));
