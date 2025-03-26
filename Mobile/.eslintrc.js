module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    extends: [
      'eslint:recommended',
      'plugin:@typescript-eslint/recommended',
      'plugin:react-hooks/recommended',
      'plugin:react/recommended'
    ],
    plugins: ['@typescript-eslint', 'react', 'react-hooks'],
    env: {
      'react-native/react-native': true,
      es2021: true,
      node: true
    },
    rules: {
      // Exemplo de regras personalizadas:
      '@typescript-eslint/no-unused-vars': 'warn',
      '@typescript-eslint/no-explicit-any': 'off',
      'react/prop-types': 'off', // não precisamos quando usamos TypeScript
      'no-console': 'warn'
    },
    settings: {
      react: {
        version: 'detect'
      }
    }
  };
  