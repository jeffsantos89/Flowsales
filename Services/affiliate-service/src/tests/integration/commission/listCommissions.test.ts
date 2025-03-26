describe('Commission API - List Commissions', () => {
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

  // Teste para listar comissões com sucesso
  it('should list all commissions successfully', () => {
    cy.request({
      method: 'GET',
      url: '/api/commission',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array');

      if (response.body.length > 0) {
        const commission = response.body[0];
        expect(commission).to.have.property('id');
        expect(commission).to.have.property('amount');
        expect(commission).to.have.property('status');
        expect(commission).to.have.property('affiliate');
      }
    });
  });

  // Teste para quando a lista de comissões estiver vazia
  it('should return an empty array if no commissions exist', () => {
    cy.request({
      method: 'GET',
      url: '/api/commission?emptyTest=true', // Parâmetro fictício para simular lista vazia
      headers: { Authorization: `Bearer ${authToken}` },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array').that.is.empty;
    });
  });

  // Teste para retorno 401 se token estiver ausente
  it('should return 401 if token is missing', () => {
    cy.request({
      method: 'GET',
      url: '/api/commission',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste para erro no servidor (500)
  it('should handle server errors gracefully', () => {
    cy.request({
      method: 'GET',
      url: '/api/commission?forceError=true', // Parâmetro fictício para simular erro
      headers: { Authorization: `Bearer ${authToken}` },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(500);
      expect(response.body).to.have.property('error');
    });
  });
});
