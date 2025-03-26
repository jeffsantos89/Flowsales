describe('Commission API - Add Commission', () => {
  let authToken: string;

  // Antes de todos os testes, realiza login para obter token
  before(() => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'admin@example.com',
        password: 'password123',
      },
    }).then((response) => {
      authToken = response.body.token;
    });
  });

  // Teste de sucesso ao adicionar comissão
  it('should add a commission successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 500,
        status: 'approved',
        affiliateId: 1,
      },
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('commission');
      expect(response.body.commission).to.have.property('id');
      expect(response.body.commission).to.have.property('amount', 500);
    });
  });

  // Teste de erro para afiliado inexistente
  it('should return 404 for non-existing affiliate ID', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 500,
        status: 'approved',
        affiliateId: 9999, // ID inexistente
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404);
      expect(response.body).to.have.property('error', 'Affiliate not found');
    });
  });

  // Teste para valores inválidos (ex.: valor negativo)
  it('should return 400 for invalid amount', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: -100,
        status: 'approved',
        affiliateId: 1,
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property('error', 'Invalid amount');
    });
  });

  // Teste para status inválido
  it('should return 400 for invalid status', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 200,
        status: 'invalid-status',
        affiliateId: 1,
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property('error', 'Invalid status');
    });
  });

  // Teste para falta de autenticação (401)
  it('should return 401 if no token is provided', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      body: {
        amount: 300,
        status: 'approved',
        affiliateId: 1,
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste para erro de conexão com o banco de dados
  it('should handle database connection error gracefully', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: {
        Authorization: `Bearer ${authToken}`,
        'X-Simulate-DB-Error': 'true', // Cabeçalho hipotético para simular erro
      },
      body: {
        amount: 400,
        status: 'approved',
        affiliateId: 1,
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(500);
      expect(response.body).to.have.property(
        'error',
        'Database connection error'
      );
    });
  });
});
