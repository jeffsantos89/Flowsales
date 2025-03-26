interface Affiliate {
  id: string;
  name: string;
  email: string;
  createdAt: string;
}

describe('Affiliate API - List Affiliates', () => {
  let authToken: string;

  // Realiza login para obter um token válido antes de todos os testes
  before(() => {
    cy.request({
      method: 'POST',
      url: '/api/auth/login',
      body: {
        email: 'admin@example.com',
        password: 'AdminPassword123!',
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('token');
      authToken = response.body.token;
    });
  });

  // Teste para listar todos os afiliados com sucesso
  it('should list all affiliates successfully', () => {
    cy.request({
      method: 'GET',
      url: '/api/affiliate',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array');
      response.body.forEach((affiliate: Affiliate) => {
        expect(affiliate).to.have.all.keys('id', 'name', 'email', 'createdAt');
      });
    });
  });

  // Teste para falha ao listar afiliados sem autenticação
  it('should fail to list affiliates without authentication', () => {
    cy.request({
      method: 'GET',
      url: '/api/affiliate',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(401);
      expect(response.body).to.have.property('error', 'Access denied');
    });
  });

  // Teste para listar afiliados com filtro (exemplo de email específico)
  it('should list affiliates filtered by email', () => {
    const emailFilter = 'johndoe@example.com';
    cy.request({
      method: 'GET',
      url: `/api/affiliate?email=${emailFilter}`,
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      response.body.forEach((affiliate: Affiliate) => {
        expect(affiliate.email).to.eq(emailFilter);
      });
    });
  });
});
