module.exports = {
  root: true,
  env: {
    node: true,
  },
  extends: [
    "plugin:vue/vue3-essential",
    "eslint:recommended",
    "@vue/typescript/recommended",
    "plugin:prettier/recommended",
  ],
  parserOptions: {
    ecmaVersion: 2020,
  },
  rules: {
    "no-console": process.env.NODE_ENV === "production" ? "warn" : "off",
    "no-debugger": process.env.NODE_ENV === "production" ? "warn" : "off",
    "@typescript-eslint/no-unused-vars": 0,
    "@typescript-eslint/no-explicit-any": "warn",
    "prettier/prettier": process.env.NODE_ENV === "production" ? "error" : "warn",
    "vue/no-v-text-v-html-on-component": "off",
  },
};
