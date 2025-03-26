module.exports = {
    root: true,
    env: {
        node: true,
        es6: true,
        browser: true,
        jest: true,
    },
    extends: [
        "eslint:recommended",
        "plugin:@typescript-eslint/recommended",
        "plugin:prettier/recommended",
        "plugin:security/recommended",
        "plugin:import/errors",
        "plugin:import/warnings",
        "plugin:import/typescript",
    ],
    parser: "@typescript-eslint/parser",
    parserOptions: {
        ecmaVersion: 2020,
        sourceType: "module",
        ecmaFeatures: {
            jsx: true,
        },
    },
    plugins: [
        "@typescript-eslint",
        "prettier",
        "security",
        "import",
    ],
    rules: {
        "@typescript-eslint/no-unused-vars": ["warn", { argsIgnorePattern: "^_" }],
        "prettier/prettier": "error",
        "no-console": "warn",
        "import/order": [
            "error",
            {
                groups: [["builtin", "external", "internal"]],
                "newlines-between": "always",
            },
        ],
        "import/no-unresolved": "error",
        "import/no-extraneous-dependencies": [
            "error",
            {
                devDependencies: ["**/*.test.ts", "**/*.spec.ts", "**/jest.setup.ts"],
            },
        ],
        "security/detect-object-injection": "off",
    },
    settings: {
        "import/resolver": {
            node: {
                extensions: [".js", ".jsx", ".ts", ".tsx"],
            },
        },
    },
};