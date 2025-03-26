import './cypress.d.ts'; // Importação das definições personalizadas

// Definição dos comandos personalizados para Cypress
export {};

import 'cypress';

declare module 'cypress' {
  interface Chainable {
    /**
     * Realiza login e armazena o token no localStorage.
     * @param email O email do usuário.
     * @param password A senha do usuário.
     * @returns O token de autenticação.
     */
    login(email: string, password: string): Chainable<string>;

    /**
     * Realiza logout, removendo o token do localStorage.
     */
    logout(): Chainable<void>;

    /**
     * Define o token de autenticação diretamente no localStorage.
     * @param token O token de autenticação.
     */
    setAuthToken(token: string): Chainable<void>;

    /**
     * Verifica se o usuário está autenticado.
     * @returns `true` se autenticado, `false` caso contrário.
     */
    isAuthenticated(): Chainable<boolean>;

    /**
     * Simula um erro 500 no servidor para testes de fallback.
     */
    simulateServerError(): Chainable<void>;
  }
}

// =======================================================
// ✅ Configurações Globais para Reset de Estado nos Testes
// =======================================================

// Reseta o banco de dados antes de cada teste
beforeEach(() => {
  cy.request('POST', '/api/test/reset-db').then((response) => {
    expect(response.status).to.eq(200);
  });
});

// Limpa os tokens e dados sensíveis após cada teste
Cypress.Commands.add('logout', function (): Cypress.Chainable<void> {
  cy.window().then((win) => win.localStorage.removeItem('authToken'));
  return cy.wrap(undefined).then(() => {});
});
cy.logout();
cy.logout();
cy.window().then((win) => win.localStorage.clear());

// =======================================================
// ✅ Comandos Customizados do Cypress
// =======================================================

// 🔑 Login: Autentica o usuário e armazena o token no localStorage
Cypress.Commands.add('login', (email: string, password: string) => {
  return cy
    .request('POST', '/api/auth/login', { email, password })
    .then((response) => {
      expect(response.status).to.eq(200);
      const token = response.body.token;
      cy.window().then((win) => win.localStorage.setItem('authToken', token));
      return cy.wrap(token);
    });
});

// 🚪 Logout: Remove o token de autenticação do localStorage
Cypress.Commands.add('logout', function (): Cypress.Chainable<void> {
  cy.window().then((win) => win.localStorage.removeItem('authToken'));
  return cy.wrap(undefined);
});

// 🔒 Define Token: Permite configurar um token de autenticação manualmente
Cypress.Commands.add('setAuthToken', (token: string) => {
  cy.window().then((win) => win.localStorage.setItem('authToken', token));
  return cy.wrap(null);
});

// 🔍 Verifica se o usuário está autenticado
Cypress.Commands.add('isAuthenticated', () => {
  return cy.window().then((win) => {
    const token = win.localStorage.getItem('authToken');
    return cy.wrap(Boolean(token));
  });
});

// 🚨 Simula Erro no Servidor (500)
Cypress.Commands.add('simulateServerError', () => {
  cy.intercept({ method: 'GET', url: '/api/*' }, { statusCode: 500 }).as(
    'serverError'
  );
  return cy.wrap(null);
});

export {};
