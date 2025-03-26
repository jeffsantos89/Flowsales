module.exports = {
    preset: 'jest-expo', // Preset da expo, que configura transform para RN
    testPathIgnorePatterns: [
      '/node_modules/',
      '/android/',
      '/ios/',
      '/.expo/',
    ],
    transformIgnorePatterns: [
      'node_modules/(?!(react-native|@react-native|expo|@expo|@unimodules|react-clone-referenced-element|@react-navigation))'
    ],
    moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
    // Exemplo de cobertura (opcional):
    collectCoverage: false,
    collectCoverageFrom: [
      'src/**/*.{ts,tsx}',
      '!src/**/*.d.ts',
    ],
    coverageDirectory: './coverage',
  };
  