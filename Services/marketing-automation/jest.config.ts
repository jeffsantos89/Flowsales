import type { Config } from '@jest/types';

const config: Config.InitialOptions = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    testMatch: ['<rootDir>/src/tests/**/*.test.ts'],
    moduleFileExtensions: ['ts', 'js', 'json'],
    transform: {
        '^.+\\.tsx?$': 'ts-jest',
    },
    setupFiles: ['<rootDir>/src/tests/setupTests.ts'],
    setupFilesAfterEnv: ['<rootDir>/src/tests/setupAfterEnv.ts'],
    collectCoverage: true,
    collectCoverageFrom: [
        'src/**/*.ts',
        '!src/**/*.d.ts',
        '!src/tests/**',
        '!src/config/**',
    ],
    coverageDirectory: 'coverage',
    coverageReporters: ['json', 'lcov', 'text', 'clover', 'html'],
    moduleNameMapper: {
        '^@/(.*)$': '<rootDir>/src/$1',
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    },
    globals: {
        'ts-jest': {
            tsconfig: '<rootDir>/tsconfig.json',
            diagnostics: {
                warnOnly: true,
            },
        },
    },
    verbose: true,
    clearMocks: true,
    resetMocks: true,
    restoreMocks: true,
    testTimeout: 30000,
    maxWorkers: '50%',
    notify: true,
    notifyMode: 'failure-change',
    reporters: [
        'default',
        ['jest-junit', { outputDirectory: 'reports/junit', outputName: 'js-test-results.xml' }],
    ],
};

export default config;
