module.exports = {
  env: {
    node: true, // Ambiente Node.js
    es6: true, // Suporte a ES6
    jest: true, // Suporte para Jest (testes)
  },
  extends: [
    'eslint:recommended', // Regras recomendadas do ESLint
    'plugin:@typescript-eslint/recommended', // Regras recomendadas para TypeScript
    'plugin:prettier/recommended', // Integração com Prettier (detecta erros de formatação)
  ],
  parser: '@typescript-eslint/parser', // Parser para TypeScript
  plugins: ['@typescript-eslint', 'prettier'], // Plugins usados
  parserOptions: {
    ecmaVersion: 2020, // Suporte a ES2020
    sourceType: 'module', // Suporte a módulos ES
  },
  rules: {
    '@typescript-eslint/no-unused-vars': 'warn', // Aviso para variáveis não usadas
    'prettier/prettier': 'error', // Erro se o código não seguir o padrão do Prettier
    'no-console': 'warn', // Aviso ao usar console.log()
    'no-debugger': 'warn', // Aviso ao usar debugger
    '@typescript-eslint/explicit-function-return-type': 'off', // Desliga obrigatoriedade de tipo explícito
    '@typescript-eslint/no-explicit-any': 'warn', // Aviso ao usar 'any'
    'sort-imports': [
      'error',
      {
        // Ordena imports alfabeticamente
        ignoreCase: true,
        ignoreDeclarationSort: true,
      },
    ],
  },
  overrides: [
    {
      files: ['**/*.test.ts', '**/*.spec.ts'],
      env: {
        jest: true, // Suporte específico para testes com Jest
      },
    },
  ],
};
