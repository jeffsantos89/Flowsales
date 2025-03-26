const express = require('express');
const logger = require('./logger');
const cfg = require('../config');
const productsRoutes = require('./routes/products');
const cartRoutes = require('./routes/cart');
const ordersRoutes = require('./routes/orders');
const errorHandling = require('./errorHandling');

function createApp() {
  const app = express();
  app.use(express.json());

  // Rotas: se quiser forçar JWT global, use app.use(jwtAuth)
  app.use('/products', productsRoutes);
  app.use('/cart', cartRoutes);
  app.use('/orders', ordersRoutes);

  // Erros
  app.use(errorHandling);

  return app;
}

function startServer() {
  const app = createApp();
  app.listen(cfg.port, () => {
    logger.info(`Store service rodando na porta ${cfg.port} (PID=${process.pid})`);
  });
}

module.exports = { createApp, startServer };
