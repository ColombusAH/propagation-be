import js from "@eslint/js";
import typescriptEslint from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import reactPlugin from "eslint-plugin-react";
import reactHooksPlugin from "eslint-plugin-react-hooks";
import reactRefreshPlugin from "eslint-plugin-react-refresh";
import globals from "globals";

export default [
    js.configs.recommended,
    {
        files: ["**/*.{ts,tsx}"],
        languageOptions: {
            parser: typescriptParser,
            parserOptions: {
                ecmaVersion: "latest",
                sourceType: "module",
                ecmaFeatures: {
                    jsx: true,
                },
            },
            globals: {
                ...globals.browser,
                ...globals.es2020,
            },
        },
        plugins: {
            "@typescript-eslint": typescriptEslint,
            react: reactPlugin,
            "react-hooks": reactHooksPlugin,
            "react-refresh": reactRefreshPlugin,
        },
        settings: {
            react: {
                version: "detect",
            },
        },
        rules: {
            ...typescriptEslint.configs.recommended.rules,
            ...reactPlugin.configs.recommended.rules,
            ...reactPlugin.configs["jsx-runtime"].rules,
            ...reactHooksPlugin.configs.recommended.rules,
            "react-refresh/only-export-components": [
                "warn",
                { allowConstantExport: true },
            ],
            "@typescript-eslint/no-unused-vars": [
                "warn",
                { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
            ],
        },
    },
    {
        ignores: ["dist", ".eslintrc.cjs", "eslint.config.js"],
    },
];
