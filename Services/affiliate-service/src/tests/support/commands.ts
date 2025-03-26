// src/tests/support/commands.ts

import 'cypress';
import { AuthToken } from './types'; // Create these types separately

// Enhanced custom commands interface
interface CustomCommands {
  login(credentials?: {
    email: string;
    password: string;
  }): Cypress.Chainable<AuthToken>;
  logout(): Cypress.Chainable<void>;
  setAuthToken(token: AuthToken): Cypress.Chainable<void>;
  isAuthenticated(): Cypress.Chainable<boolean>;
  clearCache(): Cypress.Chainable<void>;
  setCache(key: string, value: unknown): Cypress.Chainable<void>;
  getCache<T = unknown>(key: string): Cypress.Chainable<T>;
  simulateServerError(config?: {
    method?: string;
    url?: string;
    status?: number;
  }): void;
}

// Extend Cypress interface
declare global {
  namespace Cypress {
    interface Chainable<Subject = any> extends CustomCommands {}
  }
}

// Configuration constants
const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/auth/login',
    LOGOUT: '/api/auth/logout',
  },
  CACHE: {
    CLEAR: '/api/cache/clear',
    SET: '/api/cache/set',
    GET: '/api/cache/get',
  },
} as const;

const DEFAULT_CREDENTIALS = {
  email: Cypress.env('DEFAULT_USER_EMAIL') || 'johndoe@example.com',
  password: Cypress.env('DEFAULT_USER_PASSWORD') || 'Password123!',
};

// Error handling utility
const handleApiError = (error: unknown): never => {
  Cypress.log({
    name: 'API Error',
    message: error instanceof Error ? error.message : 'Unknown error',
    consoleProps: () => error as Cypress.ObjectLike,
  });
  throw error;
};

// Command implementations
Cypress.Commands.add('login', (credentials = DEFAULT_CREDENTIALS) => {
  return cy
    .request({
      method: 'POST',
      url: API_ENDPOINTS.AUTH.LOGIN,
      body: credentials,
      failOnStatusCode: true,
    })
    .then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('token');

      const token = response.body.token;
      window.localStorage.setItem('authToken', token);

      return token;
    });
});

Cypress.Commands.add('logout', () => {
  return cy
    .wrap(null)
    .then(undefined, handleApiError)
    .then(() => {
      window.localStorage.removeItem('authToken');
      return cy.request({
        method: 'POST',
        url: API_ENDPOINTS.AUTH.LOGOUT,
        failOnStatusCode: true,
      });
    })
    .then((response) => {
      expect(response.status).to.eq(200);
    })
    .catch(handleApiError);
});

Cypress.Commands.add('setAuthToken', (token: AuthToken) => {
  return cy.wrap(null).then(() => {
    if (!token) throw new Error('Auth token is required');
    window.localStorage.setItem('authToken', token);
  });
});

Cypress.Commands.add('isAuthenticated', () => {
  return cy.wrap(null).then(() => {
    const token = window.localStorage.getItem('authToken');
    return Boolean(token);
  });
});

Cypress.Commands.add('clearCache', () => {
  return cy
    .request({
      method: 'POST',
      url: API_ENDPOINTS.CACHE.CLEAR,
      failOnStatusCode: true,
    })
    .then((response) => {
      expect(response.status).to.eq(200);
    })
    .catch(handleApiError);
});

Cypress.Commands.add('setCache', (key: string, value: unknown) => {
  return cy
    .request({
      method: 'POST',
      url: API_ENDPOINTS.CACHE.SET,
      body: { key, value },
      failOnStatusCode: true,
    })
    .then((response) => {
      expect(response.status).to.eq(200);
    })
    .catch(handleApiError);
});

Cypress.Commands.add('getCache', (key: string) => {
  return cy
    .request({
      method: 'GET',
      url: `${API_ENDPOINTS.CACHE.GET}?key=${encodeURIComponent(key)}`,
      failOnStatusCode: true,
    })
    .then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('value');
      return response.body.value;
    })
    .catch(handleApiError);
});

Cypress.Commands.add(
  'simulateServerError',
  (config = { method: 'GET', url: '/api/*', status: 500 }) => {
    cy.intercept(config.method, config.url, { statusCode: config.status });
  }
);

cy.intercept(config.method || 'GET', config.url || '/api/*', {
  statusCode: config.status || 500,
});
beforeEach(() => {
  cy.wrap(null).then(() => {
    window.localStorage.clear();
  });
});

afterEach(() => {
  cy.logout();
  cy.clearCache();
});

export {};
