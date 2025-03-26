module.exports = {
    parser: '@typescript-eslint/parser',
    extends: [
        'plugin:@typescript-eslint/recommended',
        'plugin:prettier/recommended',
        'plugin:import/errors',
        'plugin:import/warnings',
        'plugin:import/typescript',
    ],
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module',
        project: './tsconfig.json',
    },
    settings: {
        'import/resolver': {
            typescript: {},
        },
    },
    rules: {
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/explicit-module-boundary-types': 'off',
        '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
        'import/order': [
            'error',
            {
                groups: [['builtin', 'external', 'internal']],
                'newlines-between': 'always',
            },
        ],
        'prettier/prettier': 'error',
    },
};
module.exports = {
    root: true,
    parser: '@typescript-eslint/parser',
    plugins: ['@typescript-eslint'],
    extends: [
      'eslint:recommended',
      'plugin:@typescript-eslint/recommended',
      'prettier'
    ],
    rules: {
      '@typescript-eslint/no-unused-vars': ['error', { 'argsIgnorePattern': '^_' }],
      'no-console': 'warn'
    }
  };
  