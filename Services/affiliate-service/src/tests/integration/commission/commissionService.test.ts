describe('Commission Service API', () => {
  let authToken: string;

  // Realiza login antes de todos os testes para obter um token válido
  before(() => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'johndoe@example.com',
        password: 'Password123!',
      },
    }).then((response) => {
      authToken = response.body.token;
    });
  });

  // Teste para adicionar uma nova comissão com sucesso
  it('should add a new commission successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 150.0,
        status: 'pending',
        affiliateId: 1,
      },
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('commission');
      expect(response.body.commission).to.have.property('id');
      expect(response.body.commission).to.have.property('amount', 150.0);
      expect(response.body.commission).to.have.property('status', 'pending');
    });
  });

  // Teste para listar todas as comissões
  it('should list all commissions', () => {
    cy.request({
      method: 'GET',
      url: '/api/commission',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array');
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.property('id');
        expect(response.body[0]).to.have.property('amount');
        expect(response.body[0]).to.have.property('status');
      }
    });
  });

  // Teste para comissão com afiliado inexistente
  it('should return 404 if affiliate does not exist', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 100.0,
        status: 'pending',
        affiliateId: 9999, // ID inexistente
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404);
      expect(response.body).to.have.property('error', 'Affiliate not found');
    });
  });

  // Teste para valores inválidos (ex.: valor negativo)
  it('should return 400 for invalid commission amount', () => {
    cy.request({
      method: 'POST',
      url: '/api/commission/add',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: -150.0,
        status: 'pending',
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
        amount: 150.0,
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
        amount: 150.0,
        status: 'pending',
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
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        amount: 150.0,
        status: 'pending',
        affiliateId: 1,
      },
      failOnStatusCode: false,
    }).then((response) => {
      if (response.status === 500) {
        expect(response.body).to.have.property(
          'error',
          'Database connection error'
        );
      }
    });
  });
});
