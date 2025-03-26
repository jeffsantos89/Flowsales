import { AppDataSource } from '../config/database';

// Inicializa o banco antes de todos os testes
beforeAll(async () => {
  await AppDataSource.initialize();
});

// Fecha conexão com o banco após todos os testes
afterAll(async () => {
  await AppDataSource.destroy();
});
