describe('Login Test', () => {
    it('should login with valid credentials', () => {
      cy.visit('/login');
      cy.get('input[name="email"]').type('admin@example.com');
      cy.get('input[name="password"]').type('password123');
      cy.get('button[type="submit"]').click();
      cy.url().should('include', '/dashboard');
    });
  });
  