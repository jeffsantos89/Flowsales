module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
  verbose: true,
  clearMocks: true, // Limpa mocks automaticamente entre os testes
  collectCoverage: true, // Coleta cobertura de código
  collectCoverageFrom: [
    'src/**/*.ts',
    '!src/**/index.ts', // Ignora arquivos de índice
    '!src/**/types/*.ts', // Ignora tipos se houver
  ],
  coverageDirectory: 'coverage', // Pasta para relatórios de cobertura
  coverageThreshold: {
    // Limiares mínimos de cobertura
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  moduleNameMapper: {
    // Mapeamento para módulos e caminhos
    '^@src/(.*)$': '<rootDir>/src/$1',
    '^@config/(.*)$': '<rootDir>/src/config/$1',
    '^@services/(.*)$': '<rootDir>/src/services/$1',
    '^@controllers/(.*)$': '<rootDir>/src/controllers/$1',
    '^@models/(.*)$': '<rootDir>/src/models/$1',
    '^@repositories/(.*)$': '<rootDir>/src/repositories/$1',
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'], // Configuração antes dos testes
  testTimeout: 30000, // Timeout maior para testes assíncronos (30s)
  maxWorkers: '50%', // Limita a quantidade de threads em execução
};
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  collectCoverage: true,
  collectCoverageFrom: [
    '**/*.{ts,tsx}',
    '!**/node_modules/**',
    '!**/tests/**',
    '!**/types/**',
    '!**/dtos/**',
    '!**/config/**',
    '!**/routes/**',
    '!**/index.ts',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov'],
};
