describe('Redis Cache Service', () => {
  const testKey = `testKey-${Date.now()}`;
  const testValue = 'testValue';

  // Teste de cache com sucesso
  it('should cache data successfully', () => {
    cy.request({
      method: 'POST',
      url: '/api/cache/set',
      body: {
        key: testKey,
        value: testValue,
        expiration: 60, // Expira em 60 segundos
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property(
        'message',
        'Data cached successfully'
      );
    });
  });

  // Teste de recuperação de cache com sucesso
  it('should retrieve cached data successfully', () => {
    cy.request(`/api/cache/get?key=${testKey}`).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property('value', testValue);
    });
  });

  // Teste de cache com expiração
  it('should expire cache after specified time', () => {
    const tempKey = `tempKey-${Date.now()}`;
    cy.request({
      method: 'POST',
      url: '/api/cache/set',
      body: {
        key: tempKey,
        value: 'temporaryValue',
        expiration: 1, // Expira em 1 segundo
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      cy.wait(2000); // Aguarda 2 segundos para garantir a expiração

      cy.request({
        method: 'GET',
        url: `/api/cache/get?key=${tempKey}`,
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(404);
        expect(res.body).to.have.property('error', 'Cache not found');
      });
    });
  });

  // Teste para chave inexistente
  it('should return 404 for non-existing cache key', () => {
    cy.request({
      method: 'GET',
      url: '/api/cache/get?key=nonExistingKey',
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(404);
      expect(response.body).to.have.property('error', 'Cache not found');
    });
  });

  // Teste para falha de conexão com o Redis
  it('should handle Redis connection error gracefully', () => {
    // Simula erro configurando uma chave inválida (caso a API suporte esse tipo de teste)
    cy.request({
      method: 'POST',
      url: '/api/cache/set',
      body: {
        key: 'invalidKey',
        value: testValue,
      },
      headers: {
        'X-Simulate-Redis-Error': 'true', // Cabeçalho hipotético para simular erro
      },
      failOnStatusCode: false,
    }).then((response) => {
      expect(response.status).to.eq(500);
      expect(response.body).to.have.property('error', 'Redis connection error');
    });
  });

  // Teste para remoção de cache
  it('should delete cached data successfully', () => {
    cy.request({
      method: 'DELETE',
      url: `/api/cache/delete?key=${testKey}`,
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.have.property(
        'message',
        'Cache deleted successfully'
      );

      // Verifica se o cache foi realmente deletado
      cy.request({
        method: 'GET',
        url: `/api/cache/get?key=${testKey}`,
        failOnStatusCode: false,
      }).then((res) => {
        expect(res.status).to.eq(404);
        expect(res.body).to.have.property('error', 'Cache not found');
      });
    });
  });
});
