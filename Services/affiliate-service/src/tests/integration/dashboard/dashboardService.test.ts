describe('Dashboard Service API', () => {
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

  // Teste para verificar se os dados do dashboard são retornados corretamente
  it('should return aggregated dashboard data', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.keys([
        'totalAffiliates',
        'totalCommissions',
        'totalEarnings',
      ]);

      // Valida os tipos dos dados
      expect(response.body.totalAffiliates).to.be.a('number');
      expect(response.body.totalCommissions).to.be.a('number');
      expect(response.body.totalEarnings).to.be.a('number');
    });
  });

  // Teste para garantir que a API retorne erro 401 se o token estiver ausente
  it('should return 401 if token is missing', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      failOnStatusCode: false, // Evita falhar o teste imediatamente
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste para garantir que a API responda dentro de um tempo aceitável
  it('should respond within an acceptable time limit', () => {
    const start = Date.now();
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then(() => {
      const duration = Date.now() - start;
      expect(duration).to.be.lessThan(2000); // Exemplo: 2 segundos como limite
    });
  });

  // Teste para verificar se o total de ganhos não retorna valor negativo
  it('should not return negative total earnings', () => {
    cy.request({
      method: 'GET',
      url: '/api/dashboard',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.body.totalEarnings).to.be.at.least(0);
    });
  });
});
