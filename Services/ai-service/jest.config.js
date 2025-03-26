const { pathsToModuleNameMapper } = require('ts-jest/utils');
const { compilerOptions } = require('./tsconfig');

module.exports = {
    preset: "ts-jest",
    testEnvironment: "node",
    testMatch: ["**/tests/**/*.test.ts"],
    verbose: true,
    collectCoverage: true,
    coverageDirectory: "coverage",
    coverageReporters: ["json", "lcov", "text", "clover"],
    moduleNameMapper: pathsToModuleNameMapper(compilerOptions.paths || {}, { prefix: '<rootDir>/' }),
    setupFilesAfterEnv: ["<rootDir>/jest.setup.js"],
    globals: {
        'ts-jest': {
            tsconfig: 'tsconfig.json',
            diagnostics: {
                warnOnly: true
            }
        }
    },
    testPathIgnorePatterns: ["/node_modules/", "/dist/"],
    transform: {
        "^.+\\.ts$": "ts-jest"
    },
    moduleFileExtensions: ["ts", "js", "json", "node"],
    reporters: [
        "default",
        ["./node_modules/jest-html-reporter", {
            pageTitle: "Test Report",
            outputPath: "reports/test-report.html",
            includeFailureMsg: true,
            includeConsoleLog: true
        }]
    ],
    cacheDirectory: ".jest/cache",
    maxWorkers: "50%",
};