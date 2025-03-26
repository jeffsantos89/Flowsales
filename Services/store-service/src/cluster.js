const cluster = require('cluster');
const os = require('os');
const logger = require('./logger');
const { startServer } = require('./server');
const cfg = require('../config');

if (cfg.cluster && cluster.isMaster) {
  logger.info(`Master ${process.pid} is running`);
  const numCPUs = os.cpus().length;
  for (let i = 0; i < numCPUs; i++) {
    cluster.fork();
  }
  cluster.on('exit', (worker, code, signal) => {
    logger.error(`Worker ${worker.process.pid} died. Spawning a new one...`);
    cluster.fork();
  });
} else {
  // Worker
  startServer();
}
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
const express = require('express');
const logger = require('./logger');
const cfg = require('../config');
const productsRoutes = require('./routes/products');
const cartRoutes = require('./routes/cart');
const ordersRoutes = require('./routes/orders');
const errorHandling = require('./errorHandling');
