// Testes de Interface (UI)
describe('Login UI Test', () => {
  it('should display login page correctly', () => {
    cy.visit('/login');
    cy.get('h1').should('contain', 'Login');
    cy.get('input[name="email"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.get('button[type="submit"]').should('exist');
  });

  it('should login with valid credentials and redirect to dashboard', () => {
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.getCookie('authToken').should('exist');
  });

  it('should display error on invalid credentials', () => {
    cy.visit('/login');
    cy.get('input[name="email"]').type('admin@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    cy.get('.error-message').should('contain', 'Invalid credentials');
  });
});

// Testes de API
describe('Auth API - Login', () => {
  let authToken: string;

  // Teste de login com credenciais válidas
  it('should login successfully and return a valid token', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'johndoe@example.com',
        password: 'Password123!',
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('token');
      authToken = response.body.token;
      expect(authToken).to.match(
        /^eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+$/
      ); // Verifica se é um JWT válido
    });
  });

  // Teste de login com senha incorreta
  it('should fail login with incorrect password', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'johndoe@example.com',
        password: 'WrongPassword!',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Invalid credentials');
    });
  });

  // Teste de login com email inválido
  it('should fail login with invalid email', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'invalid-email',
        password: 'Password123!',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property('error', 'Invalid email format');
    });
  });

  // Teste de acesso negado sem token
  it('should reject access to protected routes without token', () => {
    cy.request({
      method: 'GET',
      url: '/api/affiliate',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste de acesso com token inválido
  it('should reject access to protected routes with invalid token', () => {
    cy.request({
      method: 'GET',
      url: '/api/affiliate',
      headers: { Authorization: 'Bearer invalidToken123' },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Invalid token');
    });
  });

  // Teste de login com campos vazios
  it('should fail login with empty fields', () => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: '',
        password: '',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property(
        'error',
        'Email and password are required'
      );
    });
  });
});
