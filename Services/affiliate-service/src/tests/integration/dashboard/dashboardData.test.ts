describe('Dashboard API - Fetch Dashboard Data', () => {
  let authToken: string;

  // Login antes dos testes para obter um token válido
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

  // Teste para obter dados do dashboard com sucesso
  it('should fetch dashboard data successfully', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
    });
  });

  // Teste para verificar se as propriedades existem e têm o tipo correto
  it('should return totalAffiliates, totalCommissions, and totalEarnings with correct types', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
    }).then((response) => {
      expect(response.body)
        .to.have.property('totalAffiliates')
        .and.to.be.a('number');
      expect(response.body)
        .to.have.property('totalCommissions')
        .and.to.be.a('number');
      expect(response.body)
        .to.have.property('totalEarnings')
        .and.to.be.a('number');
    });
  });

  // Teste para erro 401 se o token estiver ausente
  it('should return 401 if token is missing', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      failOnStatusCode: false, // Evita que o teste falhe imediatamente
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste para erro 500 se algo der errado no servidor
  it('should handle server errors gracefully', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard?forceError=true',
      headers: {
        Authorization: `Bearer ${authToken}`,
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(500);
      expect(response.body).to.have.property(
        'message',
        'Internal Server Error'
      );
    });
  });
});
