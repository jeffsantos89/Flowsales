describe('Affiliate API - Create Affiliate', () => {
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

  // Teste para criação bem-sucedida de um afiliado
  it('should create a new affiliate successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'John Doe',
        email: `johndoe${Date.now()}@example.com`, // Email dinâmico para evitar conflitos
        password: 'Password123!',
      },
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.affiliate).to.have.keys([
        'id',
        'name',
        'email',
        'createdAt',
      ]);
      expect(response.body.affiliate.email).to.match(/@example\.com$/);
    });
  });

  // Teste para falha ao registrar afiliado com email existente
  it('should fail to create an affiliate with existing email', () => {
    const duplicateEmail = `duplicate${Date.now()}@example.com`;

    // Registra o afiliado pela primeira vez
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Jane Doe',
        email: duplicateEmail,
        password: 'Password123!',
      },
    }).then((response) => {
      expect(response.status).to.eq(201);
    });

    // Tenta registrar novamente com o mesmo email
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: 'Jane Doe',
        email: duplicateEmail,
        password: 'Password123!',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(409);
      expect(response.body).to.have.property('message', 'Email already exists');
    });
  });

  // Teste para falha ao registrar afiliado com dados inválidos
  it('should fail to create an affiliate with invalid data', () => {
    cy.request({
      method: 'POST',
      url: '/api/affiliate/register',
      headers: { Authorization: `Bearer ${authToken}` },
      body: {
        name: '', // Nome vazio
        email: 'invalid-email', // Email inválido
        password: 'Password123!',
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(400);
      expect(response.body).to.have.property('message');
    });
  });
});
