describe('Affiliate Service API', () => {
  let authToken: string;

  // Realiza login para obter um token válido antes de todos os testes
  before(() => {
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
    });
  });

  // Teste para registrar um novo afiliado com sucesso
  it('should register a new affiliate successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Affiliate Test',
        email: `affiliate${Date.now()}@example.com`,
        password: 'Password123!',
      },
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('affiliate');
      expect(response.body.affiliate).to.have.all.keys(
        'id',
        'name',
        'email',
        'createdAt'
      );
      expect(response.body.affiliate.email).to.match(/@example\.com$/);
    });
  });

  // Teste para tentar registrar um afiliado com email duplicado
  it('should fail to register an affiliate with duplicate email', () => {
    const duplicateEmail = 'affiliate@example.com';

    // Primeiro registro para garantir que o email exista
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Affiliate Original',
        email: duplicateEmail,
        password: 'Password123!',
      },
      failOnStatusCode: false,
    });

    // Tentativa de registrar novamente com o mesmo email
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Affiliate Duplicate',
        email: duplicateEmail,
        password: 'Password123!',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(409);
      expect(response.body).to.have.property('message', 'Email already in use');
    });
  });

  // Teste para listar todos os afiliados cadastrados
  it('should list all affiliates', () => {
    cy.request({
      method: 'GET',
      url: '/api/affiliate',
      headers: { Authorization: `Bearer ${authToken}` },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.be.an('array');
      if (response.body.length > 0) {
        expect(response.body[0]).to.have.all.keys(
          'id',
          'name',
          'email',
          'createdAt'
        );
      }
    });
  });

  // Teste para buscar um afiliado específico pelo ID
  it('should fetch a specific affiliate by ID', () => {
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Affiliate Finder',
        email: `finder${Date.now()}@example.com`,
        password: 'Password123!',
      },
    }).then((registerResponse) => {
      const affiliateId = registerResponse.body.affiliate.id;

      cy.request({
        method: 'GET',
        url: `/api/affiliate/${affiliateId}`,
        headers: { Authorization: `Bearer ${authToken}` },
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body).to.have.property('id', affiliateId);
        expect(response.body).to.have.property('name', 'Affiliate Finder');
      });
    });
  });
});
