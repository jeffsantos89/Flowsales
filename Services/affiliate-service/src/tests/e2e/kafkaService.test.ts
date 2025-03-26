import 'cypress';
import { expect } from 'chai';

declare global {
  interface Cypress {
    Chainer: Chai.AssertionStatic;
  }
}

describe('Kafka Integration Tests', () => {
  const topic = 'test-topic';
  const testMessage = 'Test Message';
  const timeout = 5000; // Timeout customizado para operações Kafka

  before(() => {
    // Configuração inicial, se necessário
    cy.request('POST', '/api/kafka/cleanup', { topic }).then((response) => {
      expect(response.status).to.eq(200);
    });
  });

  after(() => {
    // Limpeza após os testes
    cy.request('POST', '/api/kafka/cleanup', { topic }).then((response) => {
      expect(response.status).to.eq(200);
    });
  });

  it('should publish a message to Kafka successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/kafka/publish',
      body: {
        topic,
        message: testMessage,
      },
      timeout,
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('status', 'published');
    });
  });

  it('should handle publish failure gracefully', () => {
    cy.request({
      method: 'POST',
      url: '/api/kafka/publish',
      body: {
        topic: '', // Forçando um erro
        message: testMessage,
      },
      failOnStatusCode: false,
      timeout,
    }).then((response) => {
      expect(response.status).to.be.oneOf([400, 500]);
      expect(response.body).to.have.property('error');
    });
  });

  it('should consume a message from Kafka successfully', () => {
    cy.request({
      method: 'GET',
      url: `/api/kafka/consume?topic=${topic}`,
      timeout,
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('message', testMessage);
      expect(response.headers)
        .to.have.property('content-type')
        .and.include('application/json');
    });
  });

  it('should handle consume failure gracefully', () => {
    cy.request({
      method: 'GET',
      url: `/api/kafka/consume?topic=non-existent-topic`,
      failOnStatusCode: false,
      timeout,
    }).then((response) => {
      expect(response.status).to.be.oneOf([404, 500]);
      expect(response.body).to.have.property('error');
    });
  });
});
function before(callback: () => void) {
  // In Cypress, 'before' is a hook that runs once before all tests in a describe block
  // We need to delegate to Cypress's native 'before' function
  return cy.wrap({}).then(() => {
    callback();
  });
}
function after(callback: () => void) {
  return cy.wrap({}).then(() => {
    callback();
  });
}

// filepath: cypress.config.ts
import { defineConfig } from 'cypress';

export default defineConfig({
  projectId: 'your-project-id', // Optional: If you're using Cypress Cloud

  // Viewport settings
  viewportWidth: 1280,
  viewportHeight: 720,

  // Test settings
  e2e: {
    baseUrl: 'http://localhost:3000', // Your application's base URL
    specPattern: 'cypress/e2e/**/*.{js,jsx,ts,tsx}',
  },
  defaultCommandTimeout: 4000, // Default timeout for Cypress commands
  pageLoadTimeout: 60000, // Timeout for page load

  // Files and folders
  fixturesFolder: 'cypress/fixtures',
  screenshotsFolder: 'cypress/screenshots',
  videosFolder: 'cypress/videos',
  supportFolder: 'cypress/support', // Location of support files

  // Environment variables
  env: {
    // Add any environment variables your tests need here
    api_url: 'http://localhost:3001/api',
    'cypress-plugin-retries-clearAfterEach': true,
  },

  // Retry settings
  retries: {
    runMode: 2, // Number of retries in run mode
    openMode: 0, // Number of retries in open mode
  },

  // Experimental settings
  experimentalStudio: true, // Enable Cypress Studio
  experimentalInteractiveRunEvents: false, // Disable Jest adapter

  // Cypress Cloud setup
  setupNodeEvents() {
    // Implement node event listeners here (e.g., for code coverage)
  },
});
